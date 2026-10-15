"""Real nnU-Net CPU optimizer step, checkpoint publication and resume on tiny synthetic data.
Does not execute the full notebook, contact Drive, or qualify GPU/memory/performance.
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
import random
import sys
import time

def main(source, plans_file, destination):
    root = Path(destination); root.mkdir()
    os.environ.update(nnUNet_raw=str(root/"raw"), nnUNet_preprocessed=str(root/"preprocessed"),
                      nnUNet_results=str(root/"results"), nnUNet_compile="false",
                      OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2")
    import torch
    import numpy as np
    torch.set_num_threads(2); torch.manual_seed(101)
    spec=importlib.util.spec_from_file_location("exact_scientific_module",source)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m._load_science();m.check_trainer_source()
    from colab_storage_reliability import install
    from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
    plans=json.loads(Path(plans_file).read_text())
    plans["dataset_name"]="Dataset999_SYNTHETIC_CHECKPOINT_ONLY"
    cfg=plans["configurations"]["3d_fullres"]
    cfg.update(patch_size=[16,16,16],batch_size=2,median_image_size_in_voxels=[16,16,16])
    kw=cfg["architecture"]["arch_kwargs"]
    kw.update(n_stages=3,features_per_stage=[4,8,16],kernel_sizes=[[3,3,3]]*3,
              strides=[[1,1,1],[2,2,2],[2,2,2]],n_blocks_per_stage=[1,1,1],
              n_conv_per_stage_decoder=[1,1])
    dataset={"channel_names":{str(i):"noNorm"for i in range(6)},
             "labels":{"background":0,"infarct":1},"numTraining":1,"file_ending":".nii.gz"}
    try:
        nnUNetTrainer(copy.deepcopy(plans),"3d_fullres",0,dataset,torch.device("cpu"))
    except KeyError as exc:
        assert exc.args==("continue_training",)
        old_constructor_failure=True
    else:
        raise AssertionError("Old missing-continue_training control did not fail")
    class Backend:
        def __init__(self):self.value={};self.version=0;self.now=1000
        def read(self):return str(self.version),self.now,copy.deepcopy(self.value)
        def replace(self,etag,value):
            assert etag==str(self.version)
            self.value=copy.deepcopy(value);self.version+=1
    install(m)
    backend=Backend();lease=m.FitLease(backend,{"synthetic_cpu":True}).acquire()
    fit=root/"fold0";att=fit/"attempts"/lease.owner;att.mkdir(parents=True)
    cp=m.Checkpoints(fit,att,lease)
    tr=m._trainer_class()(plans,"3d_fullres",0,dataset,torch.device("cpu"))
    tr._lease=lease
    preprocessed=Path(tr.preprocessed_dataset_folder);preprocessed.mkdir(parents=True)
    np.savez_compressed(preprocessed/"synthetic.npz",data=np.zeros((6,16,16,16),dtype=np.float32),seg=np.zeros((1,16,16,16),dtype=np.int16))
    tr.initialize()
    Path(tr.output_folder).mkdir(parents=True,exist_ok=True)
    tr.log_file=str(root/"trainer.log")
    shape=(16,16,16);data=torch.randn((2,6,*shape))
    target=torch.randint(0,2,(2,1,*shape))
    targets=[torch.nn.functional.interpolate(target.float(),
        size=tuple(round(n*s)for n,s in zip(shape,scale)),mode="nearest").long()
        for scale in tr._get_deep_supervision_scales()]
    def publish(epoch):
        def write(path):
            old_epoch=tr.current_epoch;tr.current_epoch=epoch-1
            try:tr.save_checkpoint(str(path))
            finally:tr.current_epoch=old_epoch
            blob=torch.load(str(path),map_location="cpu",weights_only=False)
            blob["delivery_state"]={"python_rng":random.getstate(),"numpy_rng":np.random.get_state(),
                "torch_rng":torch.get_rng_state(),"cuda_rng":[],"measurements":[]}
            torch.save(blob,str(path))
        return cp.publish("latest",write,{"next_epoch":epoch,"total_epochs":250,"native_version":"2.8.1"})
    initial=publish(0)
    initial_blob=torch.load(str(fit/initial["path"]),map_location="cpu",weights_only=False)
    assert initial_blob["optimizer_state"]["state"]=={}
    before=next(tr.network.parameters()).detach().clone()
    tr.on_train_epoch_start()
    loss=tr.train_step({"data":data,"target":targets})
    delta=float((next(tr.network.parameters()).detach()-before).abs().max())
    assert delta>0 and np.isfinite(loss["loss"]).all()
    tr.logger.log("train_losses",float(loss["loss"]),0)
    after=publish(1)
    saved=copy.deepcopy(tr.network.state_dict());optimizer=copy.deepcopy(tr.optimizer.state_dict())
    assert optimizer["state"]
    with torch.no_grad():
        for tensor in tr.network.parameters():tensor.zero_()
    tr.optimizer.state.clear();tr.current_epoch=0
    path,record=cp.select("latest")
    tr.load_checkpoint(str(path))
    assert tr.current_epoch==1 and record==after
    assert all(torch.equal(v,saved[k])for k,v in tr.network.state_dict().items())
    for key,state in optimizer["state"].items():
        for name,val in state.items():
            actual=tr.optimizer.state_dict()["state"][key][name]
            assert torch.equal(val,actual)if torch.is_tensor(val)else val==actual
    resumed_before=next(tr.network.parameters()).detach().clone()
    resumed_loss=tr.train_step({"data":data,"target":targets})
    resumed_delta=float((next(tr.network.parameters()).detach()-resumed_before).abs().max())
    assert resumed_delta>0
    result={"status":"PASS","arm":m.K_AM,"device":"cpu","synthetic_only":True,
        "real_optimizer_updates":2,"published_then_reloaded":True,"resumed_epoch":1,
        "weights_and_optimizer_exactly_restored":True,"parameter_change":delta,
        "resumed_parameter_change":resumed_delta,"initial_optimizer_entries":0,
        "after_step_optimizer_entries":len(optimizer["state"]),
        "initial_bytes":initial["bytes"],"after_step_bytes":after["bytes"],
        "old_continue_training_control_failed":old_constructor_failure,
        "scientific_module_sha256":hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        "trainer_source_sha256":m.TRAINER_SOURCE_SHA256,
        "torch_version":torch.__version__,"nnunet_version":"2.8.1",
        "full_notebook_executed":False,"live_drive_used":False,"gpu_qualified":False}
    (root/"RESULT.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
    lease.close()

if __name__=="__main__":
    main(*sys.argv[1:])
