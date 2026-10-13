"""Initial in-call schema feedback for the distinct arm question.

Reuses the reviewed visible-only checker; does not execute scientific code,
alter attempt accounting, or replace the host checks and scientific review.
"""
from pathlib import Path
import json
from orchestrator import colab_arm_question as q, private_records as pr
RUNTIME='.colab-feedback'

def feedback_files(driver):
    from orchestrator import notebook_revision as nr, colab_preparation_scope as scope
    from orchestrator import scientific_intake as intake, colab_static_feedback as existing
    cfg=driver.config['notebook_revision']
    original,selection=scope.validate_notebook_config(driver.context,cfg)
    registry=json.loads(nr.bound(driver.context,driver.config['private_intake']))
    cases=intake.cohort((driver.context/registry['cohort']).read_bytes())
    view,manifest=nr.partition(original,selection,cases,nr.VIEW)
    bodies={'check.py':existing.CHECKER.encode(),'orchestrator/__init__.py':b'',
        **{'orchestrator/'+name+'.py':raw for name,raw in existing.runtime_libraries().items()},
        'view.txt':view,'manifest.json':q.encoded(manifest),
        'binding.json':q.encoded({'run_id':q.RUN,'analysis_registry_sha256':driver.config['private_intake']['sha256'],
            'original_sha256':nr.ORIGINAL,'view_sha256':nr.VIEW})}
    for raw in bodies.values():nr.scan(raw,cases)
    return {RUNTIME+'/'+name:raw for name,raw in bodies.items()}

def task(files):
    refs='\n'.join(name+' sha256='+q.sha(raw) for name,raw in files.items())
    return (
        "\nINITIAL AUTHOR SCHEMA FEEDBACK. Write SPEC.proposed.md and notebook.patch.json. "
        "This route uses FILE-BASED submission; no submit_author MCP tool is provided. "
        "Do not fabricate a receipt. safe-notebook-patch/v1 edits have EXACT fields "
        "unit:string cells/<integer>/source; start:integer UTF8 byte offset; "
        "end:integer byte offset (start<end); before_sha256:64 lowercase hex; "
        "replacement:STRING, never an array. All rounds patch the same bound original. "
        "After writing BOTH files run python3 -I -B .colab-feedback/check.py. "
        "Read errors, correct and rerun in this same call, at most12 local iterations. "
        "Do not edit checker or bound inputs. Patch<=80000bytes; SPEC<=12000characters. "
        "This is static schema/interface feedback only, not the requested full synthetic "
        "author sandbox and not proof tests ran. State unavailable tests honestly. "
        "Host privacy/schema/synthetic checks and independent scientific review remain. "
        "No patient payloads, provider execution or credential access. Bound files:\n"+refs+"\n")

def prepared(base):
    class Prepared(base):
        def prepare_input(self,value,stage,work):
            if self.config.get('run_id')!=q.RUN or stage!='run_spec_author':
                return super().prepare_input(value,stage,work)
            q.validate(self.store,q.RUN)
            files=feedback_files(self)
            self._pnorm_v2_feedback=files
            try:
                body,measurement=super().prepare_input(value,stage,work)
            finally:
                self.__dict__.pop('_pnorm_v2_feedback',None)
            refs=[]
            for name,raw in files.items():
                target=Path(work)/name
                pr.mkdir(target.parent,parents=True,exist_ok=True)
                q.require(not target.exists() and not target.is_symlink(),'FEEDBACK_EXISTS')
                pr.write_bytes(target,raw);target.chmod(0o400)
                refs.append({'path':name,'sha256':q.sha(raw),'bytes':len(raw)})
            return body,{**measurement,'workspace_files':[*measurement['workspace_files'],*refs]}
        def task(self,stage,value):
            text=super().task(stage,value)
            return text+task(self._pnorm_v2_feedback) if hasattr(self,'_pnorm_v2_feedback') else text
    return Prepared
