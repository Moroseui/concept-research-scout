# Research progress: pinned runtime connection

The execution draft now connects offline dependency installation to the actual fit launch and collection paths. Previously the launcher verified and mounted wheel files but did not install them. It now requires a selected interpreter and exact environment pins, installs only hash-verified binary wheels without networking, and compares the actual Python, package and CUDA versions before scientific code runs. Collection checks the preserved environment receipt and carries its observed metadata forward.

Private draft commit: a56101f4b136fecb9f02bc486d54aa97df9f1327. Final regression: 875 passed, six server-only skips, 31 passing subtests. All 29 new runtime tests ran without skips, including a native confined worker importing an actual offline-installed synthetic wheel. These tests do not claim real GPU training. The draft is not deployed or independently approved yet.

The original direct download was last observed running with 7.94 GB stored and 696 individually verified files. Final verification is pending. Actual billing reports $0.15856688 for the current download application through 19:00 UTC; this excludes the partial hour and is not final accounting. No new fit or model call was launched by this engineering work.

The next critical connections are the author-owned scientific preprocessing executor and actual runtime provisioning. The real image and dependency closure still need verification. Full server tests, independent review and genuine smoke/benchmark execution remain. Author sign-in renewal is still outstanding; engineering and retrieval continue independently.

Items 2 and 5 remain complete. Item 4 training and item 6 diagnostics remain incomplete. No new scientific result or acceptance is claimed. H2 stays archived.
