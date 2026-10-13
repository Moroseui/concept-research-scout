"""Pure synthetic fixtures for notebook module constant extraction."""
import copy
import unittest
from orchestrator import notebook_synthetic_harness as h
COVERAGE = "\ndef coverage_support(x,brain,coverage=None):\n    if coverage is not None and coverage.shape!=x.shape: raise ValueError('shape')\n    return brain & np.isfinite(x) & (coverage if coverage is not None else True), {'coverage_known':coverage is not None}\ndef zscore_in_brain(x,mask):\n    y=np.zeros_like(x)\n    v=x[mask]\n    if not len(v) or v.std()<1e-6:return y, {'fallback':'empty or constant'}\n    sd=max(float(v.std()),ZSCORE_MIN_SD)\n    y[mask]=(v-v.mean())/sd\n    return y,{'fallback':None,'sd_used':sd}\ndef histeq_in_brain(x,mask):\n    y=np.zeros_like(x);v=x[mask]\n    if not len(v) or v.std()<1e-6:return y,{'fallback':'empty or constant'}\n    y[mask]=np.searchsorted(np.sort(v),v,side='right')/len(v)\n    return y,{'fallback':None}\n"
def fixture():
    nb={'cells':[{'cell_type':'markdown','source':[]} for _ in range(23)]}
    nb['cells'][4]={'cell_type':'code','source':['ZSCORE_MIN_SD=0.01\n']}
    nb['cells'][8]={'cell_type':'code','source':[COVERAGE]}
    return nb


def exported_fixture():
    nb=fixture()
    nb['cells'][4]['source']=['# old configuration intentionally empty\n']
    nb['cells'][8]['source']=['%%writefile -a /content/sprint13_pipeline.py\n'+COVERAGE]
    nb['cells'][10]={'cell_type':'code','source':['%%writefile -a /content/sprint13_pipeline.py\nZSCORE_MIN_SD=0.01\nHISTEQ_BINS=256\n']}
    return nb

class ExportedConstantsTests(unittest.TestCase):
    def test_actual_export_layout_supplies_authored_literals(self):
        nb=exported_fixture()
        self.assertEqual(h.exported_constants(nb,8,{'coverage_support','zscore_in_brain','histeq_in_brain'}),{'ZSCORE_MIN_SD':0.01,'HISTEQ_BINS':256})
        self.assertTrue(h.test_coverage_handling(nb)['empty_constant_floor_checked'])

    def test_prior_configuration_layout_still_passes(self):
        self.assertTrue(h.test_coverage_handling(fixture())['empty_constant_floor_checked'])

    def test_no_top_level_operations_execute(self):
        nb=exported_fixture()
        nb['cells'][10]['source'][0]+="\nraise RuntimeError('must not execute')\n"
        self.assertTrue(h.test_coverage_handling(nb)['empty_constant_floor_checked'])

    def test_nonliteral_duplicate_augmented_or_annotated_constant_refuses(self):
        for statement in ["ZSCORE_MIN_SD=float('0.01')","ZSCORE_MIN_SD=0.01\nZSCORE_MIN_SD=0.02",
                          "ZSCORE_MIN_SD=0.01\nZSCORE_MIN_SD+=0.02","ZSCORE_MIN_SD:float=0.01",
                          "ZSCORE_MIN_SD,HISTEQ_BINS=(0.01,256)"]:
            nb=exported_fixture();nb['cells'][10]['source']=['%%writefile -a /content/sprint13_pipeline.py\n'+statement]
            with self.subTest(statement=statement),self.assertRaises(ValueError):h.module(nb,8)

    def test_other_export_target_cannot_supply_constants(self):
        nb=exported_fixture();nb['cells'][10]['source'][0]=nb['cells'][10]['source'][0].replace('sprint13_pipeline.py','other.py')
        with self.assertRaises(NameError):h.test_coverage_handling(nb)

    def test_redefined_helper_refuses(self):
        nb=exported_fixture();nb['cells'][10]['source'][0]+="\ndef coverage_support(x,brain,coverage=None): return brain,{}\n"
        with self.assertRaisesRegex(ValueError,'HELPER_REDEFINED'):h.module(nb,8)

    def test_wrong_science_still_fails(self):
        nb=exported_fixture();nb['cells'][8]['source'][0]=nb['cells'][8]['source'][0].replace("return brain & np.isfinite(x) & (coverage if coverage is not None else True)","return brain")
        with self.assertRaises(AssertionError):h.test_coverage_handling(nb)

if __name__=='__main__':unittest.main()
