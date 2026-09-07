# Transport-review import finding — reproduced against original source

The first combined transport review at `29eec99a` returned REQUEST_CHANGES,
inferring that a dependency-only PYTHONPATH prevents the frozen runner from
importing `orchestrator.campaign`. Its review explicitly states the runner itself
was not supplied in that packet. Preserve that review and its original protocol.

The actual frozen runner at `d6a1184`, SHA-256
`d54e3ea5c45c0d47fe8bace014058e1660d92b72abc36cc2fdc077acae3d47b0`, computes
its repository root and executes `sys.path.insert(0,str(ROOT))` before the campaign
import. The existing preflight uses exec_module, so these top-level statements run.
No scientific execution or selection function is invoked merely by importing it.

A real subprocess test copied those exact Git bytes plus the two required package
files into a fresh directory, provided only a separate dependencies directory in
PYTHONPATH, excluded the original checkout/user site, and successfully imported the
runner and the campaign module from that frozen directory. No cohort/member files
were even present. All four transport tests pass, including actual sparse Git
acquisition and preservation/refusal of a changed source file.

Disposition: the proposed import defect was not reproduced; exact source and the
subprocess test contradict its premise. No redundant import workaround or frozen
code change is applied. Fresh Claude follow-up must resolve this finding before
the preparation receipt can be used. The rejected verdict remains recorded.
