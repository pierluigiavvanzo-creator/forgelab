import unittest

from forgelab.quality import review_patch, security_review_patch


class QualityTests(unittest.TestCase):
    def test_out_of_scope_patch_is_rejected(self):
        patch = "diff --git a/bad.py b/bad.py\n--- a/bad.py\n+++ b/bad.py\n+change\n"
        self.assertEqual(review_patch(patch, {"good.py"})["status"], "FAIL")

    def test_secret_in_added_line_is_rejected(self):
        patch = "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n+api_key='abcdefghijklmnop1234'\n"
        self.assertEqual(security_review_patch(patch)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
