import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def run_cli(self, left, right, *args):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            before, after = folder / "before.jsonl", folder / "after.jsonl"
            before.write_text(left, encoding="utf-8")
            after.write_text(right, encoding="utf-8")
            return subprocess.run([sys.executable, "-m", "jsonl_diff.cli", "--left", str(before),
                                   "--right", str(after), *args], capture_output=True, text=True)

    def test_exit_zero_for_same_snapshot(self):
        result = self.run_cli('{"id":"a"}', '{"id":"a"}')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["counts"]["unchanged"], 1)

    def test_exit_one_for_changes_and_ignore_field_flag(self):
        left, right = '{"id":"a","updated":1}', '{"id":"a","updated":2}'
        result = self.run_cli(left, right)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["changed"][0]["fields"], ["updated"])
        self.assertEqual(self.run_cli(left, right, "--ignore-field", "updated").returncode, 0)

    def test_invalid_input_exits_two_without_partial_report(self):
        result = self.run_cli('{"id":"a"}', '{"id":"a"}\nnot json')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("line 2", result.stderr)

    def test_output_file_is_created_once_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            result = self.run_cli('{"id":"a"}', '{"id":"b"}', "--output", str(output))
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(json.loads(output.read_text())["added"], ["b"])
            saved = output.read_bytes()
            repeated = self.run_cli("", "", "--output", str(output))
            self.assertEqual(repeated.returncode, 2)
            self.assertEqual(output.read_bytes(), saved)


if __name__ == "__main__":
    unittest.main()
