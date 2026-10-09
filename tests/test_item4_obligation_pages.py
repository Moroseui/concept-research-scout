import copy,json
import pytest
from orchestrator import context_budget as b,manual_context as m
from test_context_budget import root,add_obligation,save_manifest


def setup(root,kind='adverse finding'):
 add_obligation(root,kind)
 p=root/b.PROJECT/'obligations.json';v=json.loads(p.read_text());row=v['obligations'][-1]
 text=('Complete synthetic finding with Unicode '+chr(233)+' and '+chr(0x1f642)+'.\n')*4500
 (root/'new-operator-record.md').write_text(text)
 row['scope']['idea_ids']=['sprint13b-execution'];row['text']=text
 row['source'].update(sha256=b.sha(text.encode()),end=len(text.encode()))
 p.write_text(json.dumps(v));save_manifest(root)
 return text


def assemble(root,pages,stage='run_spec_author',ideas=None,artifacts='unchanged artifacts'):
 return b.assemble(root,project='isles24-prediction',idea_ids=ideas or ['sprint13b-execution'],
  stage=stage,task='Read all mandatory pages',artifacts=artifacts,obligation_files=pages)


@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
def test_exact_large_findings_all_delivered_scanned_hashed_and_readonly(root,tmp_path,stage):
 setup(root);args=(root,'isles24-prediction',['sprint13b-execution'],stage)
 pages=m.obligation_pages(*args)
 original='\n\n'.join(b.open_obligation_text(r) for r in b.obligations(*args)).encode()
 assert len(original)>200000 and b''.join(raw for _,raw in pages)==original
 assert all(0<len(raw)<=12000 for _,raw in pages)
 body,measurement=assemble(root,pages,stage)
 assert measurement['characters']<200000 and 'TEST-STOP' in measurement['open_obligations']
 assert b.sha(original) in body and all(d['path'] in body for d,_ in pages)
 work=tmp_path/'readable-pages';delivered=m._workspace_files(work,pages)
 assert b''.join((work/d['path']).read_bytes() for d in delivered)==original
 assert all((work/d['path']).stat().st_mode & 0o222==0 for d in delivered)
 b.dispatch_preflight(root,project='isles24-prediction',idea_ids=['sprint13b-execution'],stage=stage,text=body)
 with pytest.raises(b.ContextTooLarge):assemble(root,pages,stage,artifacts='x'*200000)


@pytest.mark.parametrize('fault',['missing','reordered','changed-byte','changed-hash','changed-path','changed-source','empty','wrong-stage','wrong-item'])
def test_no_truncation_substitution_or_unscoped_file_route(root,fault):
 setup(root);pages=m.obligation_pages(root,'isles24-prediction',['sprint13b-execution'],'run_spec_author')
 if fault=='missing':pages.pop()
 elif fault=='reordered':pages.reverse()
 elif fault=='changed-byte':pages[0]=(pages[0][0],pages[0][1]+b'x')
 elif fault=='changed-hash':pages[0][0]['sha256']='0'*64
 elif fault=='changed-path':pages[0][0]['path']='evidence/wrong.txt'
 elif fault=='changed-source':(root/'new-operator-record.md').write_text('changed')
 elif fault=='empty':pages=[]
 with pytest.raises((b.ContextError,ValueError)):
  assemble(root,pages,stage='result_interpretation_author' if fault=='wrong-stage' else 'run_spec_author',
   ideas=['P001'] if fault=='wrong-item' else None)


def test_real_stop_still_blocks_even_with_all_originals_delivered(root):
 setup(root,'stop');pages=m.obligation_pages(root,'isles24-prediction',['sprint13b-execution'],'run_spec_author')
 body,_=assemble(root,pages)
 with pytest.raises(b.ContextError,match='SCOPED_STOP'):
  b.dispatch_preflight(root,project='isles24-prediction',idea_ids=['sprint13b-execution'],stage='run_spec_author',text=body)


def test_full_original_scanned_before_page_boundaries(root,monkeypatch):
 from orchestrator import git_publication as gp
 setup(root);pages=m.obligation_pages(root,'isles24-prediction',['sprint13b-execution'],'run_spec_author')
 seen=[];original=gp.scan
 def scan(name,raw):seen.append((name,raw));return original(name,raw)
 monkeypatch.setattr(gp,'scan',scan);assemble(root,pages)
 assert ('context/open-obligations.txt',b''.join(raw for _,raw in pages)) in seen
 assert all((descriptor['path'],raw) in seen for descriptor,raw in pages)
