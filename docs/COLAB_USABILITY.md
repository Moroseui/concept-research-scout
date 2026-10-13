# Colab notebook usability requirement

All user interaction must finish in the first approximately two minutes of Run all, before dependency installation, preprocessing or training. Put unavoidable existing Drive/API authorization and any browser-dependent notebook capture in one clearly labelled first executable cell. Print exactly **All logins done, you can leave now** only after they succeed. If setup fails, do not print that line or begin expensive work.

No later cell may call an interactive login, remount flow, browser notebook request, setting prompt or supervised continuation. Later loss of access must produce a bounded error, not wait for the operator. Google may require both existing Drive and API authorizations; front-load both without extracting, copying or changing credentials.

For synthetic trainer checks, mount Drive in the parent first so compact evidence preservation needs no late login. The actual worker must retain equivalent or stronger no-Drive/no-credential/network protections, demonstrated by synthetic positive and negative controls and independent implementation review. Do not simply remove its no-Drive check. Fail before expensive work if the provider cannot supply the reviewed boundary.

Keep one preconfigured notebook per arm, sequential folds0-4, automatic checkpoint resume and completed-fold skipping. Scientific changes belong to the system author and scientific reviewer. Infrastructure packaging needs opposite-family implementation review. Test exact scientific payload preservation and the absence of later browser calls. Existing accepted trainer evidence is not repeated merely for a login-ordering change.
