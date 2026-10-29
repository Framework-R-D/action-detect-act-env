import os
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).parents[1] / ".github/workflows/guardrail-audit-alert.yaml"


def workflow_script():
    content = WORKFLOW.read_text()
    match = re.search(r"^        run: \|\n((?:          .*\n|\n)+)", content, re.MULTILINE)
    if match is None:
        raise AssertionError("Could not find the guardrail workflow script")
    return textwrap.dedent(match.group(1))


class GuardrailAlertTests(unittest.TestCase):
    def run_workflow_script(self, merged_at, run_started_at):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            curl_marker = temp_path / "curl-called"
            gh = temp_path / "gh"
            gh.write_text("#!/bin/sh\nprintf '%s' \"$PR_PAGES\"\n")
            gh.chmod(0o755)
            curl = temp_path / "curl"
            curl.write_text("#!/bin/sh\ntouch \"$CURL_MARKER\"\n")
            curl.chmod(0o755)

            environment = os.environ | {
                "PATH": f"{temp_dir}:{os.environ['PATH']}",
                "PR_PAGES": (
                    '[[{"merged_at":"'
                    + merged_at
                    + '","merge_commit_sha":"sha","base":{"ref":"main",'
                    '"repo":{"full_name":"Framework-R-D/action-detect-act-env"}}}]]'
                ),
                "CURL_MARKER": str(curl_marker),
                "GH_TOKEN": "test-token",
                "SLACK_URL": "https://example.invalid",
                "COMMIT_MSG": "test",
                "PUSH_SHA": "sha",
                "FORCED_PUSH": "false",
                "RUN_STARTED_AT": run_started_at,
                "REPO_NAME": "Framework-R-D/action-detect-act-env",
                "ACTOR": "test",
            }
            subprocess.run(
                ["bash", "-e", "-o", "pipefail", "-c", workflow_script()],
                check=True,
                env=environment,
                capture_output=True,
                text=True,
            )
            return curl_marker.exists()

    def test_restoring_old_pr_merge_still_alerts(self):
        self.assertTrue(
            self.run_workflow_script(
                "2026-10-28T19:00:00Z",
                "2026-10-29T19:30:00Z",
            )
        )

    def test_current_pr_merge_suppresses_alert(self):
        self.assertFalse(
            self.run_workflow_script(
                "2026-10-29T19:00:00Z",
                "2026-10-29T19:03:00Z",
            )
        )


if __name__ == "__main__":
    unittest.main()
