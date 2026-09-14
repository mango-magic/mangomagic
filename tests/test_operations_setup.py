"""Isolated Bash 3.2 integration tests; never modify the repository's starter/.

Run: python3 -B -m unittest discover -s tests -p 'test_operations_setup.py' -v
"""

import importlib.util
import os
from pathlib import Path
import shutil
import shlex
import select
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build-operations-installer.py"
BASH = os.environ.get("MANGOMAGIC_TEST_BASH", "/bin/bash")
spec = importlib.util.spec_from_file_location("operations_builder", BUILDER)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class OperationsSetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="operations test ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        self.destination = self.root / "folder with spaces" / "AI Operations"
        self.starter = self.root / "starter fixture"
        self.starter.mkdir()
        self.templates = {
            "START_HERE.md": b"# Start here\nPaste this onboarding prompt.\n",
            "AGENTS.md": b"Local project instructions.\n",
            "roles/Sales Lead/README.md": b"# Sales\n",
            "roles/Sales Lead/run.sh": b"#!/bin/bash\nprintf 'hello\\n'\n",
            "roles/Finance/README.md": b"# Finance\n",
            "empty.md": b"",
            "no-final-newline.md": "Mangoes 🥭\nsecond line".encode(),
            "whitespace.md": b"\n\t leading  \r\nback\\slash\n\n\n",
            ".codex/agents/sales.toml": b'name = "sales"\n',
            ".gitignore": b"private/\n",
        }
        for name, data in self.templates.items():
            path = self.starter / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (self.starter / "roles/Sales Lead/run.sh").chmod(0o755)
        self.script = self.root / "setup-operations.sh"
        self.rebuild()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        # Allow only the stock tools needed for local file setup. No inherited
        # credentials, startup hooks, Python, Git, app CLI, curl or real Finder.
        for name in ("cat", "mkdir", "chmod", "mktemp", "link", "rm"):
            (self.bin / name).symlink_to(shutil.which(name, path="/usr/bin:/bin"))
        self.open_log = self.root / "open.log"
        self.mock("open", 'printf "%s\\n" "$@" >> "$OPEN_LOG"\n')
        self.mock("uname", 'printf "Darwin\\n"\n')
        self.env = {
            "HOME": str(self.home), "PATH": str(self.bin), "LC_ALL": "C",
            "OPEN_LOG": str(self.open_log),
        }
        config = self.home / ".codex" / "config.toml"
        config.parent.mkdir()
        config.write_text("# existing global config\n")
        self.home_before = self.snapshot(self.home)

    def mock(self, name, body):
        target = self.bin / name
        if target.is_symlink():
            target.unlink()  # Never write through a test utility's symlink.
        target.write_text("#!/bin/bash\n" + body)
        target.chmod(0o755)

    def rebuild(self):
        self.script.write_text(builder.render(self.starter), encoding="utf-8")

    @staticmethod
    def snapshot(root):
        return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mode)
                for p in root.rglob("*") if p.is_file()}

    def run_setup(self, *args, piped=False, source=None, default_args=True, env=None):
        options = ["--destination", str(self.destination), "--no-open"] if default_args else []
        command = [BASH, "--noprofile", "--norc"]
        if piped:
            command += ["-s", "--"]
        else:
            command += [str(self.script)]
        result = subprocess.run(
            command + options + list(args),
            input=(source if source is not None else self.script.read_bytes().decode("utf-8")) if piped else "",
            text=True, capture_output=True, env=self.env if env is None else env,
            cwd=self.root, timeout=10,
        )
        self.assertNotIn("command not found", result.stderr)
        return result

    def assert_success(self, result):
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def assert_failure(self, result):
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("Next steps:", result.stdout)
        self.assertFalse(self.open_log.exists())

    def test_stock_bash_syntax(self):
        result = subprocess.run([BASH, "--noprofile", "--norc", "-n", str(self.script)],
                                env=self.env, capture_output=True, text=True, timeout=5)
        self.assert_success(result)

    def test_install_bytes_spaces_modes_and_no_global_changes(self):
        result = self.run_setup()
        self.assert_success(result)
        for name, data in self.templates.items():
            self.assertEqual(data, (self.destination / name).read_bytes(), name)
        self.assertTrue((self.destination / "roles/Sales Lead/run.sh").stat().st_mode & 0o111)
        self.assertFalse((self.destination / "START_HERE.md").stat().st_mode & 0o111)
        self.assertEqual(self.home_before, self.snapshot(self.home))
        self.assertFalse(self.open_log.exists())
        self.assertIn("local folder project", result.stdout)
        self.assertIn("START_HERE.md", result.stdout)
        self.assertIn("verify which project-local agent definitions", result.stdout)
        self.assertIn("No workers were launched", result.stdout)

    def test_rerun_preserves_user_edits_modes_and_only_restores_missing(self):
        self.assert_success(self.run_setup())
        edited = self.destination / "roles/Sales Lead/run.sh"
        edited.write_text("# User changed this\n")
        edited.chmod(0o600)
        extra = self.destination / "user notes.txt"
        extra.write_text("Keep me")
        before = self.snapshot(self.destination)
        self.assert_success(self.run_setup(piped=True))
        self.assertEqual(before, self.snapshot(self.destination))
        (self.destination / "empty.md").unlink()
        result = self.run_setup()
        self.assert_success(result)
        self.assertIn("Created 1 file(s)", result.stdout)
        self.assertEqual(before, self.snapshot(self.destination))

    def test_curl_pipe_stdin_without_prompting(self):
        self.assert_success(self.run_setup(piped=True))
        self.assertEqual(self.templates["START_HERE.md"], (self.destination / "START_HERE.md").read_bytes())

    def test_failed_partial_write_is_cleaned_and_retry_installs_complete_file(self):
        hook = self.root / "fail-write.sh"
        hook.write_text('''printf() {
    if [ "$1" = '%s' ] && [ "${2:-}" = '# Start here' ]; then
        builtin printf '%s' 'partial output'
        builtin printf '%s\\n' 'INJECTED_WRITE_FAILURE' >&2
        return 1
    fi
    builtin printf "$@"
}
''')
        result = self.run_setup(env=dict(self.env, BASH_ENV=str(hook)))
        self.assert_failure(result)
        self.assertIn("INJECTED_WRITE_FAILURE", result.stderr)
        self.assertFalse((self.destination / "START_HERE.md").exists())
        self.assertEqual([], list(self.destination.rglob(".operations-setup.*")))
        self.assert_success(self.run_setup(piped=True))
        self.assertEqual(self.templates["START_HERE.md"], (self.destination / "START_HERE.md").read_bytes())
        self.assertEqual([], list(self.destination.rglob(".operations-setup.*")))

    def test_permission_failure_does_not_publish_or_leave_staging_files(self):
        self.mock("chmod", "exit 1\n")
        self.assert_failure(self.run_setup())
        self.assertEqual({}, self.snapshot(self.destination))
        self.assertEqual([], list(self.destination.rglob(".operations-setup.*")))

    def test_exclusive_publish_refuses_raced_files_directories_and_symlinks(self):
        real_link = shlex.quote(shutil.which("link", path="/usr/bin:/bin"))
        for kind, action in [
            ("file", 'printf "%s" "raced user content" > "$2"'),
            ("directory", 'mkdir "$2"'),
            ("symlink", '"$SYMLINK_HELPER" "$2"'),
        ]:
            with self.subTest(kind=kind):
                outside = self.root / "outside"
                outside.mkdir(exist_ok=True)
                helper = self.root / "make-symlink"
                helper.write_text("#!" + sys.executable + "\nimport os, sys\nos.symlink(" + repr(str(outside)) + ", sys.argv[1])\n")
                helper.chmod(0o755)
                self.mock("link", action + '\nprintf "%s" "$2" > "$RACE_LOG"\nexec ' + real_link + ' "$@"\n')
                log = self.root / "race-target"
                result = self.run_setup(env=dict(self.env, SYMLINK_HELPER=str(helper), RACE_LOG=str(log)))
                self.assert_failure(result)
                target = Path(log.read_text())
                if kind == "file":
                    self.assertEqual(b"raced user content", target.read_bytes())
                elif kind == "directory":
                    self.assertEqual([], list(target.iterdir()))
                else:
                    self.assertTrue(target.is_symlink())
                    self.assertEqual([], list(outside.iterdir()))
                self.assertEqual([], list(self.destination.rglob(".operations-setup.*")))
                shutil.rmtree(self.destination)

    def test_paths_rechecked_after_staging(self):
        hook = self.root / "race-during-write.sh"
        hook.write_text('''printf() {
    if [ "$1" = '%s' ] && [ "${2:-}" = '# Start here' ]; then
        mkdir "$RACED_TARGET"
    fi
    builtin printf "$@"
}
''')
        target = self.destination / "START_HERE.md"
        result = self.run_setup(env=dict(self.env, BASH_ENV=str(hook), RACED_TARGET=str(target)))
        self.assert_failure(result)
        self.assertIn("Not a regular file:", result.stderr)
        self.assertEqual([], list(target.iterdir()))
        self.assertEqual([], list(self.destination.rglob(".operations-setup.*")))

    def test_truncated_pipe_cannot_start_setup(self):
        source = self.script.read_text().rsplit('main "$@"', 1)[0].rsplit("}", 1)[0]
        self.assert_failure(self.run_setup(piped=True, source=source))
        self.assertFalse(self.destination.exists())

    def test_default_destination(self):
        self.assert_success(self.run_setup("--no-open", default_args=False, piped=True))
        self.assertTrue((self.home / "Documents/AI Operations/START_HERE.md").is_file())
        self.assertFalse(self.open_log.exists())

    def test_relative_destination(self):
        self.assert_success(self.run_setup("--destination", "relative folder", "--no-open", default_args=False))
        self.assertTrue((self.root / "relative folder/START_HERE.md").is_file())

    def test_help_and_bad_arguments_do_not_write(self):
        for options, success in [(["--help"], True), (["--unknown"], False),
                                 (["--destination"], False), (["--destination", ""], False),
                                 (["--destination", "--no-open"], False), (["positional"], False)]:
            with self.subTest(options=options):
                result = self.run_setup(*options, default_args=False, piped=True)
                (self.assert_success if success else self.assert_failure)(result)
                self.assertEqual(self.home_before, self.snapshot(self.home))
                self.assertFalse(self.destination.exists())

    def test_directory_and_file_collisions_fail_before_writing(self):
        for relative, kind in [("", "file"), ("roles", "file"),
                               ("roles/Sales Lead", "file"), ("START_HERE.md", "directory")]:
            with self.subTest(relative=relative, kind=kind):
                target = self.destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                if kind == "file":
                    target.write_bytes(b"keep collision")
                else:
                    target.mkdir()
                before = self.snapshot(self.destination) if self.destination.is_dir() else {}
                self.assert_failure(self.run_setup())
                if self.destination.is_dir():
                    self.assertEqual(before, self.snapshot(self.destination))
                    shutil.rmtree(self.destination)
                else:
                    self.assertEqual(b"keep collision", self.destination.read_bytes())
                    self.destination.unlink()

    def test_fifo_file_target_is_refused_without_hanging(self):
        self.destination.mkdir(parents=True)
        os.mkfifo(self.destination / "START_HERE.md")
        self.assert_failure(self.run_setup())
        self.assertFalse((self.destination / "AGENTS.md").exists())

    def test_symlink_roots_targets_and_ancestors_including_dangling(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "keep.md").write_bytes(b"outside remains unchanged")
        for relative in ("", "START_HERE.md", "roles", "roles/Sales Lead"):
            for dangling in (False, True):
                with self.subTest(relative=relative, dangling=dangling):
                    target = self.destination / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.symlink_to(outside / "missing" if dangling else outside)
                    self.assert_failure(self.run_setup(piped=True))
                    self.assertEqual(["keep.md"], [p.name for p in outside.iterdir()])
                    target.unlink()
                    if self.destination.exists():
                        self.assertFalse((self.destination / "AGENTS.md").exists())
                        shutil.rmtree(self.destination)

    def test_root_symlink_with_trailing_slash_or_dot_is_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.destination.parent.mkdir()
        self.destination.symlink_to(outside)
        for suffix in ("/", "/.", "/./"):
            result = self.run_setup("--destination", str(self.destination) + suffix)
            self.assert_failure(result)
        self.assertEqual([], list(outside.iterdir()))

    def test_literal_shell_injection_in_markdown_and_filename(self):
        # The deliberately executable-looking Markdown must remain byte data.
        marker = self.root / "INJECTED"
        body = ("$(touch '" + str(marker) + "')\n`touch '" + str(marker) + "'`\n"
                "${HOME}\nEOF\nOPERATIONS_DATA\n'\"\\\n").encode()
        name = "literal ' $(touch INJECTED) `touch INJECTED`.md"
        (self.starter / name).write_bytes(body)
        # Force a genuine delimiter collision to exercise delimiter selection.
        class FakeHash:
            def hexdigest(self):
                return "COLLISION"
        original = builder.hashlib.sha256
        try:
            builder.hashlib.sha256 = lambda data: FakeHash()
            (self.starter / "delimiter.md").write_text("OPERATIONS_DATA_COLLISION\n")
            self.rebuild()
        finally:
            builder.hashlib.sha256 = original
        # Even if injected code executes, touch is a test-owned observable mock.
        self.mock("touch", 'printf "injected" > "$HOME/INJECTED"\n')
        self.assert_success(self.run_setup(piped=True))
        self.assertEqual(body, (self.destination / name).read_bytes())
        self.assertFalse(marker.exists())
        self.assertEqual(self.home_before, self.snapshot(self.home))
        self.assertEqual(b"OPERATIONS_DATA_COLLISION\n", (self.destination / "delimiter.md").read_bytes())

    def test_finder_only_on_mac_and_not_with_no_open(self):
        self.assert_success(self.run_setup("--destination", str(self.destination), default_args=False))
        self.assertEqual(str(self.destination) + "\n", self.open_log.read_text())
        self.open_log.unlink()
        self.mock("uname", 'printf "Linux\\n"\n')
        self.assert_success(self.run_setup("--destination", str(self.destination), default_args=False))
        self.assertFalse(self.open_log.exists())

    def test_banner_plain_when_redirected(self):
        result = self.run_setup()
        self.assert_success(result)
        self.assertIn("ManyMangoes", result.stdout)
        self.assertIn("Data + AI + Automation", result.stdout)
        self.assertNotIn("\x1b", result.stdout)

    def test_banner_colours_only_for_tty_without_no_color(self):
        for no_color in (None, "", "1"):
            with self.subTest(no_color=no_color):
                master, slave = os.openpty()
                try:
                    env = dict(self.env)
                    if no_color is not None:
                        env["NO_COLOR"] = no_color
                    result = subprocess.run(
                        [BASH, "--noprofile", "--norc", str(self.script), "--no-open",
                         "--destination", str(self.destination)],
                        stdin=subprocess.DEVNULL, stdout=slave, stderr=subprocess.PIPE,
                        env=env, cwd=self.root, timeout=10,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    output = b""
                    # macOS may discard queued PTY output when the last slave
                    # closes. Drain it while our slave descriptor is still open.
                    while select.select([master], [], [], 0.05)[0]:
                        chunk = os.read(master, 4096)
                        if not chunk:
                            break
                        output += chunk
                    self.assertEqual(no_color is None, b"\x1b[" in output)
                    self.assertIn(b"ManyMangoes", output)
                finally:
                    os.close(master)
                    if slave is not None:
                        os.close(slave)

    def test_builder_determinism_and_cli_executable_output(self):
        before = builder.render(self.starter)
        for path in self.starter.rglob("*"):
            os.utime(path, (1000, 1000))
        (self.starter / "unused empty directory").mkdir()
        self.assertEqual(before, builder.render(self.starter))
        result = subprocess.run([sys.executable, "-B", str(BUILDER), "--starter", str(self.starter),
                                 "--output", str(self.script)], capture_output=True, text=True, timeout=10)
        self.assert_success(result)
        self.assertEqual(before.encode(), self.script.read_bytes())
        self.assertEqual(0o755, self.script.stat().st_mode & 0o777)

    def test_builder_rejects_links_binary_special_and_empty_inputs(self):
        invalid = self.root / "invalid fixture"
        invalid.mkdir()
        with self.assertRaises(ValueError):
            builder.render(invalid)

    def test_builder_rejects_output_symlink_without_touching_target(self):
        for dangling in (False, True):
            with self.subTest(dangling=dangling):
                target = self.root / ("missing target" if dangling else "unrelated file")
                if not dangling:
                    target.write_bytes(b"must stay unchanged")
                    target.chmod(0o600)
                output = self.root / "output-link.sh"
                output.symlink_to(target)
                result = subprocess.run(
                    [sys.executable, "-B", str(BUILDER), "--starter", str(self.starter),
                     "--output", str(output)], capture_output=True, text=True, timeout=10,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("output symlink refused", result.stderr)
                self.assertTrue(output.is_symlink())
                if dangling:
                    self.assertFalse(target.exists())
                else:
                    self.assertEqual(b"must stay unchanged", target.read_bytes())
                    self.assertEqual(0o600, target.stat().st_mode & 0o777)
                self.assertEqual([], list(self.root.glob(".operations-build-*")))
                output.unlink()

    def test_builder_rejects_binary_symlink_and_special_template_files(self):
        invalid = self.root / "invalid fixture"
        invalid.mkdir()
        target = invalid / "bad.md"
        for data in (b"nul\0", b"\xff"):
            target.write_bytes(data)
            with self.assertRaises((ValueError, UnicodeError)):
                builder.render(invalid)
        target.unlink()
        target.symlink_to(self.starter)
        with self.assertRaises(ValueError):
            builder.render(invalid)
        target.unlink()
        os.mkfifo(target)
        with self.assertRaises(ValueError):
            builder.render(invalid)

    def test_shipped_installer_matches_current_starter(self):
        starter = ROOT / "starter"
        if not starter.is_dir():
            self.skipTest("Other workers have not supplied starter/ yet")
        self.assertEqual(builder.render(starter).encode(), (ROOT / "setup-operations.sh").read_bytes(),
                         "Rebuild with python3 scripts/build-operations-installer.py")

    def test_shipped_installer_installs_real_starter_and_preserves_rerun(self):
        starter = ROOT / "starter"
        if not starter.is_dir():
            self.skipTest("Other workers have not supplied starter/ yet")
        self.script.write_bytes((ROOT / "setup-operations.sh").read_bytes())
        self.assert_success(self.run_setup(piped=True))
        expected = {p.relative_to(starter): p.read_bytes() for p in starter.rglob("*") if p.is_file()}
        actual = {p.relative_to(self.destination): p.read_bytes()
                  for p in self.destination.rglob("*") if p.is_file()}
        self.assertEqual(expected, actual)
        self.assertIn(Path("START_HERE.md"), actual)
        self.assertIn(Path(".gitignore"), actual)
        self.assertTrue(any(str(p).startswith(".codex/agents/") for p in actual))
        edited = self.destination / "START_HERE.md"
        edited.write_text("User-owned onboarding edits\n")
        before = self.snapshot(self.destination)
        self.assert_success(self.run_setup())
        self.assertEqual(before, self.snapshot(self.destination))
        self.assertEqual(self.home_before, self.snapshot(self.home))
        self.assertFalse(self.open_log.exists())


if __name__ == "__main__":
    unittest.main()
