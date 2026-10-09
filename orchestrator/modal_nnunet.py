"""Connect durable progress to native nnU-Net 2.8.1 save/load, not a second trainer.

Called by the reviewed per-fit package after controller admission. Training
settings and environment are bound by the package. This adapter deliberately
avoids nnU-Net's missing-checkpoint --continue fallback to a fresh fit.
"""
from pathlib import Path
import types
from orchestrator.modal_fit_progress import file_hash

TRAINER_SOURCE_SHA256 = '7096efb2040135eb60df3c8bf39cdbcc373e299671fcee365b3aff2f4da4dfbd'


def verify_native_source():
    from importlib.metadata import version
    import inspect
    from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
    if version('nnunetv2') != '2.8.1' or file_hash(inspect.getfile(nnUNetTrainer)) != TRAINER_SOURCE_SHA256:
        raise ValueError('NNUNET_NATIVE_SOURCE_CHANGED')


def run_fit(trainer, progress, *, initial, save_every, segment, interruption=None):
    """The caller holds progress.writer throughout; real smoke must prove resume.

    The native optimizer/scaler state and next epoch are retained. nnU-Net's
    polynomial scheduler uses that epoch when the next training epoch starts.
    Native checkpoints do not preserve every random/augmentation worker state;
    resumed training is not claimed to be bitwise identical to uninterrupted.
    """
    verify_native_source()
    progress._guard()
    if type(save_every) is not int or save_every not in {1, 5, 10}:
        raise ValueError('NNUNET_CHECKPOINT_INTERVAL')
    if trainer.is_ddp or trainer.local_rank != 0 or trainer.disable_checkpointing:
        raise ValueError('NNUNET_SINGLE_FIT_CHECKPOINT_REQUIRED')
    if type(trainer.num_epochs) is not int or trainer.num_epochs < 1:
        raise ValueError('NNUNET_EPOCH_BOUND')
    trainer.save_every = save_every
    original_save = trainer.save_checkpoint

    def durable_save(self, filename):
        name = Path(filename).name
        kinds = {'checkpoint_latest.pth': 'latest', 'checkpoint_best.pth': 'best',
                 'checkpoint_final.pth': 'final'}
        if name not in kinds:
            raise ValueError('NNUNET_CHECKPOINT_NAME')
        epoch = self.current_epoch + 1  # Native 2.8.1 save_checkpoint contract.
        if type(epoch) is not int or not 0 <= epoch <= self.num_epochs:
            raise ValueError('NNUNET_CHECKPOINT_EPOCH')
        return progress.publish(kinds[name], lambda path: original_save(str(path)),
                                metadata={'next_epoch': epoch, 'total_epochs': self.num_epochs,
                                          'native_version': '2.8.1'})

    trainer.save_checkpoint = types.MethodType(durable_save, trainer)
    try:
        if initial:
            if trainer.current_epoch != 0:
                raise ValueError('NNUNET_INITIAL_EPOCH')
            trainer.initialize()
            # Preserve initial weights/optimizer before the first paid epoch, so
            # even an interruption before epoch one never creates new weights.
            trainer.current_epoch = -1
            try:
                trainer.save_checkpoint('checkpoint_latest.pth')
            finally:
                trainer.current_epoch = 0
            mode, epoch = 'initial', 0
        else:
            key = 'final' if (progress.root / 'final.json').exists() else 'latest'
            path, record = progress.select(key)
            meta = record['metadata']
            if (not isinstance(meta, dict) or set(meta) != {'next_epoch', 'total_epochs', 'native_version'} or
                    type(meta['next_epoch']) is not int or not 0 <= meta['next_epoch'] <= trainer.num_epochs or
                    meta['total_epochs'] != trainer.num_epochs or meta['native_version'] != '2.8.1' or
                    (key == 'final' and meta['next_epoch'] != trainer.num_epochs)):
                raise ValueError('NNUNET_RESUME_METADATA')
            trainer.load_checkpoint(str(path))
            epoch = trainer.current_epoch
            if epoch != meta['next_epoch']:
                raise ValueError('NNUNET_LOADED_EPOCH_CHANGED')
            mode = 'validation-only' if key == 'final' else 'resume'
        progress.training_log(trainer.log_file, segment=segment)
        progress.receipt('segment-started', {'segment': segment, 'mode': mode,
                          'epoch_resumed_from': epoch, 'interruption': interruption,
                          'bitwise_replay_claimed': False})
        if mode != 'validation-only':
            trainer.run_training()
        # Verify the final checkpoint before spending effort on validation.
        _, final = progress.select('final')
        if final['metadata']['next_epoch'] != trainer.num_epochs:
            raise ValueError('NNUNET_FINAL_EPOCH')
        trainer.perform_actual_validation(True)
        progress.receipt('training-and-validation-complete', {'segment': segment,
                          'final_sha256': final['sha256'], 'epoch': trainer.num_epochs})
        return {'mode': mode, 'epoch_resumed_from': epoch, 'final_sha256': final['sha256']}
    finally:
        trainer.save_checkpoint = original_save


def execute_fit(manifest):
    """Per-fit worker entrypoint; admission and package approval stay controller-side.

    The new item4 package calls this instead of the Colab checkpoint copier.
    It requires the provider's private v2 output mount, never a host credential.
    No preprocessing, source download, package install, or budget retry occurs.
    """
    import hashlib
    import importlib.metadata
    import os
    import json
    import sys
    import torch
    from nnunetv2.paths import nnUNet_preprocessed
    from nnunetv2.run.run_training import get_trainer_from_args
    from orchestrator.modal_fit_progress import FitProgress, encoded, identifier
    verify_native_source()
    required = {'schema', 'fit_id', 'binding', 'mode', 'segment', 'interruption',
                'volume_version', 'environment', 'trainer', 'save_every'}
    if not isinstance(manifest, dict) or set(manifest) != required or manifest['schema'] != 'modal-nnunet-fit/v1':
        raise ValueError('NNUNET_FIT_MANIFEST')
    if manifest['mode'] not in {'INITIAL', 'RESUME'} or manifest['volume_version'] != 2:
        raise ValueError('NNUNET_FIT_MODE_OR_VOLUME')
    mount = Path('/progress')
    if not mount.is_mount() or mount.is_symlink():
        raise ValueError('NNUNET_PERSISTENT_MOUNT_REQUIRED')
    expected = manifest['environment']
    packages = ('nnunetv2', 'torch', 'numpy', 'nibabel', 'batchgeneratorsv2', 'dynamic-network-architectures')
    actual = {'python': sys.version, 'cuda': torch.version.cuda,
              'packages': {name: importlib.metadata.version(name) for name in packages}}
    if expected != actual or hashlib.sha256(encoded(actual)).hexdigest() != manifest['binding']['environment_sha256']:
        raise ValueError('NNUNET_FIT_ENVIRONMENT_CHANGED')
    config = manifest['trainer']
    if not isinstance(config, dict) or set(config) != {'dataset', 'configuration', 'fold', 'name', 'plans'}:
        raise ValueError('NNUNET_TRAINER_CONFIG')
    for key in ('dataset', 'configuration', 'name', 'plans'):
        identifier(config[key])
    if config['fold'] != manifest['binding']['fold']:
        raise ValueError('NNUNET_FOLD_BINDING')
    plans = Path(str(nnUNet_preprocessed)) / config['dataset'] / (config['plans'] + '.json')
    if file_hash(plans) != manifest['binding']['plans_sha256']:
        raise ValueError('NNUNET_PLANS_CHANGED')
    progress = FitProgress(mount, manifest['fit_id'], manifest['binding'])
    initial = manifest['mode'] == 'INITIAL'
    with progress.writer(initial=initial):
        # _EnvPath in pinned 2.8.1 resolves this dynamically. Set it before the
        # constructor writes logs, not merely check the output after creation.
        os.environ['nnUNet_results'] = str(progress.root / 'work')
        trainer = get_trainer_from_args(config['dataset'], config['configuration'], config['fold'],
                                        config['name'], config['plans'], not initial)
        # The package directs nnUNet_results into this fit's own work directory.
        # Refuse a shared output root before any training/validation can run.
        output = Path(trainer.output_folder).resolve()
        if not output.is_relative_to(progress.root / 'work'):
            raise ValueError('NNUNET_SHARED_OUTPUT_REFUSED')
        return run_fit(trainer, progress, initial=initial, save_every=manifest['save_every'],
                       segment=manifest['segment'], interruption=manifest['interruption'])


def main():
    import argparse
    import json
    from orchestrator import private_records
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()
    path = private_records.check(args.manifest)
    result = execute_fit(json.loads(path.read_bytes()))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
