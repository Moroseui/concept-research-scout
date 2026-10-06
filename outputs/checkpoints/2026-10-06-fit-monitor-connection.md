# Fit monitoring connection

The implementation draft now connects the experiment driver to native training logs and committed checkpoint metadata. The worker records the exact log for each fit segment; the controller does not guess filenames. Startup without a registered log waits, while disappearance after observed progress refuses. A proven stall preserves its terminal checkpoint evidence and charge. Repeated checks do not terminate again or restart a fit.

The exact draft commit aed393a06d26d52c24a1375fe788841edbfe5bba passed 810 relevant tests and 31 subtests; six server-only checks were skipped locally. Connected tests exercised driver, monitor, terminal checkpoint reader and accounting with synthetic provider storage and clocks. They do not establish actual GPU training. This draft is not installed and still requires the ordinary integrated review and server checks.

Automatic resumed dispatch remains to be connected, along with reviewed preprocessing and execution provisioning. No GPU fit or directions diagnostic has run.

The same direct development retrieval job was confirmed live at 18:29 UTC, with 234 file-verification receipts and approximately 1.90 GB stored. Download completion is not yet established. No new model call or paid job was started during this engineering work. Dedicated author sign-in renewal remains outstanding; engineering and retrieval continue independently.
