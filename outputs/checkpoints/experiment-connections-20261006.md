# Experiment execution connections ? 6 October 2026

M4 is still in progress. No new experiment or training run completed at this checkpoint.

The development branch now connects failed-job cleanup to the real executor and
connects compute admission to the experiment owner created by the driver. Failed
outcomes and reserved costs remain preserved. An observation timeout never
counts as a failed job or permission to launch another one.

The notebook execution interface now exports the existing writefile module,
imports it in the synthetic sandbox, and runs tests supplied by the scientific
author alongside the existing notebook checks. Review and packaging bind that
same module. The controller supplies no scientific methods or conclusions.

The final local regression passed 265 tests; five native tests were unavailable
locally. The server then passed 27 tests with no skips, including the actual
exported-module test in the existing sandbox. These are engineering checks,
not experiment results. This source is still a draft pending full integration,
independent review and installation.

The separate download-recovery candidate passed 5,839 tests in its full server
suite; its second suite was still running at the recorded observation. One
gated watcher can submit its single independent review after both pass. It
cannot install the change or start a download. The original failed attempt and
reservation remain preserved.

Next dependencies are the reviewed retrieval recovery and the experiment's
actual preprocessing, dispatch, collection and interpretation connections.
The scientific author and reviewer retain ownership of the notebook adaptation.
No additional operator decision is currently pending. Private source history,
data, review packets, raw records and infrastructure details are excluded here.
