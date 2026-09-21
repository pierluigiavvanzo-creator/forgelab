import tempfile
import unittest
from pathlib import Path

from forgelab.artifacts import ArtifactStore


class PatchArtifactByteTests(unittest.TestCase):
    def test_changes_patch_preserves_lf_bytes_exactly(self):
        content = (
            "diff --git a/a.py b/a.py\n"
            "--- a/a.py\n"
            "+++ b/a.py\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+new\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            target = ArtifactStore(Path(folder)).write_text("Changes.patch", content)
            payload = target.read_bytes()
        self.assertEqual(payload, content.encode("utf-8"))
        self.assertNotIn(b"\r\n", payload)

    def test_changes_patch_preserves_explicit_input_bytes(self):
        content = "one\r\ntwo\r\n"
        with tempfile.TemporaryDirectory() as folder:
            target = ArtifactStore(Path(folder)).write_text("Changes.patch", content)
            payload = target.read_bytes()
        self.assertEqual(payload, content.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()