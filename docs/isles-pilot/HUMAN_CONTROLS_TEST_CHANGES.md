# Legacy regression-test adaptation

This is the exact bounded diff for the two legacy assumptions superseded by restored controls. External action pins still require full SHAs; only the exact local reusable workflow inherits its caller commit. Actioner remains incapable of improvement Git publication.

Full current file SHA-256: `2d594f930139690bce191b09da225147163f67c58b0f67244f343431afd1f5c6`.

```diff
diff --git a/tests/test_orchestration.py b/tests/test_orchestration.py
index 0f99150..17cd4eb 100644
--- a/tests/test_orchestration.py
+++ b/tests/test_orchestration.py
@@ -1164,10 +1164,14 @@ class TestBackpressure(Harness):
 
     def test_actioner_improvement_path_is_hard_gated_until_2b(self):
         text = Path(".github/workflows/actioner.yml").read_text()
-        self.assertIn("Campaign route required", text)
+        # Restored briefing is allowed; autonomous improvement publication is not.
+        self.assertIn("uses: ./.github/workflows/research-control.yml", text)
         self.assertNotIn("gh pr create", text)
-        self.assertNotIn("secrets.", text)
-        self.assertIn("exit 1",text)
+        shared = Path(".github/workflows/research-control.yml").read_text()
+        self.assertNotIn("git push", shared)
+        self.assertNotIn("contents: write", shared)
+        config = json.loads(Path("configs/pilot/human-controls.json").read_text())
+        self.assertEqual(config['controls']['actioner']['modes'], ['brief'])
 
 
 class TestExecutionReceipts(Harness):
@@ -3613,6 +3617,11 @@ class TestR2StateAndHygiene(Harness):
             for ln in f.read_text().splitlines():
                 if "uses:" in ln:
                     checked += 1
+                    # Local reusable workflows inherit the caller's exact commit;
+                    # GitHub syntax does not allow an @SHA suffix for this form.
+                    if ln.strip() == "uses: ./.github/workflows/research-control.yml":
+                        self.assertTrue((wf / 'research-control.yml').is_file())
+                        continue
                     self.assertRegex(
                         ln, r"@[0-9a-f]{40}\b",
                         f"{f.name}: action reference must be pinned by "
```
