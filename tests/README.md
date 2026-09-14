# Offline installer integration tests

From the repository root, run:

```sh
python3 -B -m unittest discover -s tests -p 'test_install.py' -v
```

Only Python's standard library and Bash are needed. The default shell is
`/bin/bash`, which is Bash 3.2 on macOS. To test another installed Bash 3.2 binary:

```sh
MANGOMAGIC_TEST_BASH=/path/to/bash-3.2 python3 -B -m unittest discover -s tests -p 'test_install.py' -v
```

The suite snapshots `install.sh` without editing it. Each case runs that snapshot
in its own subprocess and temporary directory, with fresh HOME, TMPDIR, XDG
directories, and a replacement PATH. Environment variables from the caller are
not inherited. Network, Ollama, AppleScript/JXA, app launch, process lookup,
sleep, and temporary-file operations are mocked. Only an explicit list of text
utilities uses host binaries. There is no fallback to the host PATH. Unexpected
commands fail the case. Process killing, privilege escalation, and nested shell
installation are trap commands; source guards also reject absolute binaries and
PATH overrides before any installer execution. The Ollama mock is always present,
so the installed-app CLI fallback is never reached. A test-owned temporary
`BASH_ENV` hook advances Bash's `SECONDS` on fake `sleep` calls; deadline tests do
not spend 30 real seconds waiting. No caller startup hooks are inherited.

The stdin test supplies the script through a pipe to `bash -s --`, just as the
documented curl pipeline does, without making a network request. Fake interactive
commands deliberately read stdin to expose accidental consumption of the script.
Other cases inject misleading success text alongside nonzero pull/registration
statuses, graceful quit failures, quit timeouts, reopen failures, and missing
vision. Zero-status registration cancellation and failed or incomplete inference
responses are also rejected. Completed answers do not need a magic word. `--no-restart`, unsupported platforms, and CLI
validation are covered.

The metadata helper is mocked at its JXA `check MODEL` / `smoke MODEL` / `repair MODEL` boundary.
A wrapper with empty capabilities succeeds when its remote base resolves to
verified vision/thinking/tools. A missing-vision or unresolved base makes the
helper fail and must prevent readiness. These shell tests verify the installer's
handling of the helper contract; they do not test the helper's parsing, remote
resolution, or actual ChatGPT catalog writes.

Each test run reads a fresh installer snapshot, so rerun after the owner finishes
editing. No real installer download, Ollama operation, app quit, restart, or user
configuration write occurs.

The exact homepage repair command is also executed in the isolated harness,
including a failed download that leaves a complete script on disk. It must not
execute that failed download. Live response validation has pure fixture checks
in `test_catalog.js`; the shell fixture only verifies the JXA contract.
