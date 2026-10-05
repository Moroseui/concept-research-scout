# ---------------- CONFIG ----------------
DRIVE_BASE = "/content/drive/MyDrive/isles-pilot"
CACHE_DIR = f"{DRIVE_BASE}/feature-cache-2mm-v2"
SPRINT8_RUN_DIR = f"{DRIVE_BASE}/sprint8-seeds-features-PRIVATE/run-875c56c278"        # completed tree run (r3, continued by r4)
SPRINT9_RUN_DIR = f"{DRIVE_BASE}/sprint9-unet-PRIVATE/run-0a60362503"                   # completed FULL-protocol network run (not a -SMOKE directory)
OUT_BASE = f"{DRIVE_BASE}/sprint10-comparison-PRIVATE"
FEATURE_CFG = {"target_mm": 2.0, "vessel_pct": 98.0, "core_thr": 0.30, "penumbra_tmax": 6.0, "schema": "isles24-features-2mm-v2"}
REPO_URL, REPO_COMMIT = "https://github.com/Moroseui/concept-research-scout", "c17281a11dd2ed15e59cc38bbb526fb6c466b145"
MAP_SHUFFLE, MAP_SEED = 101, 1
PRIVATE_INPUT_DIR = f"{DRIVE_BASE}/sprint10-inputs-PRIVATE"
SPLIT_MANIFEST_PATH = f"{PRIVATE_INPUT_DIR}/split_manifest.csv"
SPLIT_MANIFEST_SHA256 = "da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843"
EXCLUSIONS = {"path": f"{PRIVATE_INPUT_DIR}/excluded_cases.json", "sha256": "ee8d4f96b0c16620450c0e7e2e6a56993d2ee68e20913c78a1bb8fe7af0f1ab2", "count": 1}
PROB_TOL = 1e-6                                                                              # score files must lie within [0 - tol, 1 + tol]
CODE_VERSION = "sprint10-r2-exclusion-reference-v1"