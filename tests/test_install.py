"""Offline installer integration tests using Bash, fake app/CLI tools, and a temp HOME.

Run from the repository root:
    python3 -B -m unittest discover -s tests -p 'test_install.py' -v
"""

from dataclasses import dataclass
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


TESTS = Path(__file__).resolve().parent
INSTALLER = TESTS.parent / "install.sh"
FIXTURE = TESTS / "fixtures" / "installer_tool.py"
MODEL = "mangomagic/mangomagic-7.1"
BASH = Path(os.environ.get("MANGOMAGIC_TEST_BASH", "/bin/bash")).resolve()
ANSI = re.compile(r"\x1b\[[0-9;]*m")
READY = re.compile(r"MangoMagic[^\n]*\bis ready\b|installation (?:complete|successful)", re.I)
FORBIDDEN_TOOLS = {"pkill", "killall", "kill", "sudo", "brew", "launchctl", "sh", "bash", "env"}
MOCK_TOOLS = FORBIDDEN_TOOLS | {
    "ollama", "curl", "osascript", "open", "pgrep", "uname", "sw_vers", "sleep",
    "mktemp", "rm", "mkdir", "python", "python3", "defaults", "plutil", "ps",
}
# These utilities only process text in the inspected installer. No system PATH
# is appended: every other external command is absent or an explicit trap.
TEXT_TOOLS = {"cat", "grep", "tail", "head", "sed", "awk", "tr", "cut", "wc", "sort", "uniq", "basename", "dirname"}


@dataclass
class InstallResult:
    status: int
    output: str
    calls: list
    state: dict

    def phase(self, name):
        return [call for call in self.calls if call.get("phase") == name]


class InstallerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not BASH.is_file():
            raise unittest.SkipTest("Bash is required; set MANGOMAGIC_TEST_BASH to a Bash 3.2 binary")
        # Freeze a read-only snapshot so concurrent installer edits cannot mix
        # contracts within one suite. Re-running picks up the owner's new file.
        cls.source = INSTALLER.read_text()
        cls.source_sha256 = hashlib.sha256(cls.source.encode()).hexdigest()

    def assert_safe_source(self, source):
        code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
        # The usage text documents /bin/bash but does not execute it.
        code = re.sub(r"<<'USAGE'\n.*?\nUSAGE", "<<'USAGE'\nUSAGE", code, flags=re.S)
        # Fail closed before execution if a rewrite could bypass the fake PATH.
        # App lookup paths are data, but absolute executable paths are not allowed.
        guards = (
            (r"/(?:usr/)?s?bin/", "Absolute binaries bypass the fake PATH"),
            (r"/(?:opt|Applications|System)/[^\s\"']*/(?:bin|MacOS)/", "Absolute binaries bypass mocks"),
            (r"\b(?:export\s+)?PATH\s*=", "Installer must preserve the isolated PATH"),
            (r"\bcommand\s+-p\b", "command -p bypasses the isolated PATH"),
            (r"(?:^|[;&|\n])\s*(?:builtin\s+)?(?:kill|eval|source|enable)\b", "Unsafe shell builtin bypasses mocks"),
        )
        for pattern, message in guards:
            match = re.search(pattern, code)
            if match:
                self.fail(message + ": " + repr(match.group(0).strip()))

    def run_installer(self, *args, scenario=None, piped=False, site_command=None):
        self.assert_safe_source(self.source)
        with tempfile.TemporaryDirectory(prefix="mangomagic installer test-") as temporary:
            root = Path(temporary).resolve()
            home = root / "home"
            bindir = root / "bin"
            for directory in (home, bindir, root / "tmp", root / "Applications" / "ChatGPT.app"):
                directory.mkdir(parents=True)
            (root / "scenario.json").write_text(json.dumps(scenario or {}))
            (root / "state.json").write_text(json.dumps({"running": (scenario or {}).get("running", True)}))
            (root / "calls.jsonl").touch()
            fixture = bindir / "mock_tool"
            fixture.write_text("#!" + sys.executable + "\n" + FIXTURE.read_text().split("\n", 1)[1])
            fixture.chmod(0o755)
            for command in MOCK_TOOLS:
                (bindir / command).symlink_to(fixture)
            for command in TEXT_TOOLS:
                executable = shutil.which(command, path="/usr/bin:/bin")
                self.assertIsNotNone(executable, "Missing text utility " + command)
                (bindir / command).symlink_to(executable)
            if site_command:
                (bindir / "bash").unlink()
                (bindir / "bash").symlink_to(BASH)
                (root / "installer-source.sh").write_text(self.source)
            clock = root / "mock-clock.sh"
            clock.write_text('sleep() { SECONDS=$((SECONDS + $1)); command sleep "$@"; }\n')
            # No inherited credentials, shell startup hooks, Ollama endpoints,
            # app preferences, proxies, or access to the user's HOME/config.
            environment = {
                "HOME": str(home), "PATH": str(bindir), "TMPDIR": str(root / "tmp"),
                "XDG_CONFIG_HOME": str(home / ".config"), "XDG_CACHE_HOME": str(home / ".cache"),
                "LANG": "C", "LC_ALL": "C", "TERM": "dumb", "NO_COLOR": "1",
                "MANGOMAGIC_TEST_ROOT": str(root), "PYTHONDONTWRITEBYTECODE": "1",
                # Only this test-owned startup hook is supplied. It advances
                # Bash's real deadline variable when the fake sleep is called.
                "BASH_ENV": str(clock),
            }
            argv = [str(BASH), "--noprofile", "--norc"]
            if site_command:
                argv += ["-c", site_command]
            elif piped:
                argv += ["-s", "--", *args]
            else:
                copy = root / "install.sh"
                copy.write_text(self.source)
                argv += [str(copy), *args]
            try:
                process = subprocess.run(
                    argv, input=self.source if piped else "", text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    cwd=home, env=environment, timeout=15,
                )
            except subprocess.TimeoutExpired as error:
                self.fail("Installer hung in isolated subprocess: " + str(error.output))
            calls = [json.loads(line) for line in (root / "calls.jsonl").read_text().splitlines()]
            result = InstallResult(process.returncode, ANSI.sub("", process.stdout), calls, json.loads((root / "state.json").read_text()))
            unexpected = [call for call in calls if "unexpected" in call]
            self.assertEqual([], unexpected, result.output + "\n" + json.dumps(unexpected, indent=2))
            self.assertFalse(FORBIDDEN_TOOLS.intersection(call["tool"] for call in calls), result.output)
            self.assertNotIn("command not found", result.output, "A new dependency needs an explicit mock")
            return result

    def assert_failed(self, result):
        self.assertNotEqual(0, result.status, result.output)
        self.assertNotRegex(result.output, READY)

    def assert_no_restart(self, result):
        self.assertEqual([], result.phase("quit"), result.output)
        self.assertEqual([], result.phase("reopen"), result.output)

    def assert_configured(self, result):
        self.assertEqual(1, len(result.phase("pull")), result.output)
        self.assertEqual(1, len(result.phase("registration")), result.output)
        self.assertEqual(1, len(result.phase("metadata_check")), result.output)
        self.assertEqual(1, len(result.phase("metadata_repair")), result.output)
        self.assertEqual(1, len(result.phase("inference")), result.output)
        self.assertTrue(result.state.get("catalog_repaired"), result.output)

    def test_bash_syntax(self):
        with tempfile.TemporaryDirectory(prefix="mangomagic-syntax-test-") as home:
            result = subprocess.run(
                [str(BASH), "--noprofile", "--norc", "-n"], input=self.source,
                text=True, capture_output=True, timeout=5,
                env={"HOME": home, "PATH": "", "LC_ALL": "C"},
            )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_no_broad_process_killing(self):
        code = "\n".join(line for line in self.source.splitlines() if not line.lstrip().startswith("#"))
        self.assertNotRegex(code, r"\b(?:pkill|killall)\b")

    def test_curl_pipe_stdin_completes_without_interactive_input(self):
        result = self.run_installer(piped=True)
        self.assertEqual(0, result.status, result.output)
        self.assertRegex(result.output, READY)
        self.assert_configured(result)
        readers = [call for call in result.calls if "stdin_bytes" in call]
        self.assertTrue(readers)
        self.assertTrue(all(call["stdin_bytes"] == 0 for call in readers), json.dumps(readers, indent=2))
        self.assertEqual(1, len(result.phase("quit")))
        self.assertEqual(1, len(result.phase("reopen")))

    def test_pull_failure_cannot_be_masked_by_success_output_or_pipeline(self):
        for piped in (False, True):
            with self.subTest(piped=piped):
                result = self.run_installer(scenario={"pull_failure": True}, piped=piped)
                self.assert_failed(result)
                self.assertIn("MOCK_PULL_FAILURE", result.output)
                self.assertEqual([], result.phase("registration"))
                self.assertEqual([], result.phase("metadata_repair"))
                self.assert_no_restart(result)

    def test_registration_failure_cannot_be_masked_by_added_message(self):
        for piped in (False, True):
            with self.subTest(piped=piped):
                result = self.run_installer(scenario={"registration_failure": True}, piped=piped)
                self.assert_failed(result)
                self.assertIn("MOCK_REGISTRATION_FAILURE", result.output)
                self.assertEqual([], result.phase("metadata_repair"))
                self.assert_no_restart(result)

    def test_zero_status_registration_cancellation_never_claims_ready(self):
        result = self.run_installer(scenario={"registration_cancelled": True})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("registration")))
        self.assertEqual([], result.phase("metadata_repair"))
        self.assert_no_restart(result)

    def test_inference_failure_with_ready_stdout_never_registers(self):
        result = self.run_installer(scenario={"inference_failure": True})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("inference")))
        self.assertEqual([], result.phase("registration"))
        self.assert_no_restart(result)

    def test_empty_inference_never_registers(self):
        result = self.run_installer(scenario={"inference_empty": True})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("inference")))
        self.assertEqual([], result.phase("registration"))
        self.assert_no_restart(result)

    def test_completed_api_response_without_magic_word_still_configures(self):
        result = self.run_installer()
        self.assertEqual(0, result.status, result.output)
        self.assert_configured(result)
        self.assertNotIn("Reply only READY", self.source)

    def test_exact_homepage_repair_command_registers_and_restarts(self):
        page = (INSTALLER.parent / "index.html").read_text()
        command = html.unescape(re.search(r'<pre id="repair-command"[^>]*>(.*?)</pre>', page, re.S)[1])
        for failed_download in (False, True):
            with self.subTest(failed_download=failed_download):
                result = self.run_installer(site_command=command, scenario={"installer_download_failure": failed_download})
                self.assertEqual(1, len(result.phase("installer_download")))
                if failed_download:
                    self.assert_failed(result)
                    self.assertEqual([], result.phase("registration"))
                    self.assert_no_restart(result)
                else:
                    self.assertEqual(0, result.status, result.output)
                    self.assert_configured(result)
                    self.assertEqual(1, len(result.phase("quit")))
                    self.assertEqual(1, len(result.phase("reopen")))

    def test_successful_restart_quits_then_reopens_exact_app(self):
        result = self.run_installer()
        self.assertEqual(0, result.status, result.output)
        self.assertRegex(result.output, READY)
        self.assert_configured(result)
        phases = [call.get("phase") for call in result.calls]
        self.assertLess(phases.index("metadata_check"), phases.index("registration"))
        self.assertLess(phases.index("metadata_repair"), phases.index("quit"))
        self.assertLess(phases.index("quit"), phases.index("reopen"))
        self.assertEqual(1, len(result.phase("quit")))
        self.assertEqual(1, len(result.phase("reopen")))
        self.assertTrue(result.state["running"])

    def test_quit_refusal_never_forces_exit_or_claims_ready(self):
        result = self.run_installer(scenario={"quit_failure": True})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("quit")))
        self.assertEqual([], result.phase("reopen"))
        self.assertTrue(result.state["running"])

    def test_quit_acknowledgment_without_exit_times_out_safely(self):
        result = self.run_installer(scenario={"quit_stuck": True})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("quit")))
        self.assertEqual([], result.phase("reopen"))
        self.assertTrue(result.state["running"])

    def test_reopen_failure_never_claims_ready(self):
        result = self.run_installer(scenario={"open_failure": True})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("reopen")))
        self.assertFalse(result.state["running"])

    def test_successful_open_without_running_app_never_claims_ready(self):
        result = self.run_installer(scenario={"open_stuck": True})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("reopen")))
        self.assertFalse(result.state["running"])

    def test_no_restart_flag_configures_without_quit_or_open(self):
        for piped in (False, True):
            with self.subTest(piped=piped):
                result = self.run_installer("--no-restart", piped=piped)
                self.assertEqual(0, result.status, result.output)
                self.assert_configured(result)
                self.assert_no_restart(result)
                self.assertNotRegex(result.output, READY)
                self.assertTrue(result.state["running"])
                self.assertRegex(result.output, r"(?i)restart|reopen|quit")

    def test_unsupported_platform_stops_before_model_or_app_changes(self):
        for platform in ("Linux", "MINGW64_NT-10.0"):
            with self.subTest(platform=platform):
                result = self.run_installer(scenario={"platform": platform}, piped=True)
                self.assert_failed(result)
                self.assertFalse(any(call["tool"] in {"ollama", "curl", "osascript", "open"} for call in result.calls), result.output)
                self.assertRegex(result.output, r"(?i)macOS|Darwin|unsupported")

    def test_missing_wrapper_caps_accept_verified_remote_base(self):
        result = self.run_installer(scenario={"wrapper_caps": [], "base_caps": ["vision", "thinking", "tools"], "base_resolved": True})
        self.assertEqual(0, result.status, result.output)
        self.assertRegex(result.output, READY)
        self.assert_configured(result)
        check = result.phase("metadata_check")[0]
        self.assertEqual([], check["wrapper_caps"])
        self.assertTrue(check["base_resolved"])

    def test_resolved_base_without_vision_never_claims_ready(self):
        result = self.run_installer(scenario={"wrapper_caps": [], "base_caps": ["thinking", "tools"]})
        self.assert_failed(result)
        self.assertIn("vision", result.output.lower())
        self.assertEqual(1, len(result.phase("metadata_check")))
        self.assertEqual([], result.phase("registration"))
        self.assertEqual([], result.phase("metadata_repair"))
        self.assert_no_restart(result)

    def test_unresolved_remote_base_never_claims_ready(self):
        result = self.run_installer(scenario={"wrapper_caps": [], "base_resolved": False})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("metadata_check")))
        self.assertEqual([], result.phase("registration"))
        self.assert_no_restart(result)

    def test_catalog_repair_failure_never_restarts_or_claims_ready(self):
        result = self.run_installer(scenario={"repair_failure": True})
        self.assert_failed(result)
        self.assertEqual(1, len(result.phase("registration")))
        self.assertEqual(1, len(result.phase("metadata_repair")))
        self.assert_no_restart(result)

    def test_helper_download_failure_never_registers_or_claims_ready(self):
        result = self.run_installer(scenario={"download_failure": True})
        self.assert_failed(result)
        self.assertEqual([], result.phase("registration"))
        self.assert_no_restart(result)

    def test_help_is_side_effect_free_and_documents_no_restart(self):
        result = self.run_installer("--help", piped=True)
        self.assertEqual(0, result.status, result.output)
        self.assertIn("--no-restart", result.output)
        self.assertEqual([], result.calls)

    def test_unknown_option_fails_before_side_effects(self):
        result = self.run_installer("--definitely-invalid", piped=True)
        self.assert_failed(result)
        self.assertEqual([], result.calls)


if __name__ == "__main__":
    unittest.main()
