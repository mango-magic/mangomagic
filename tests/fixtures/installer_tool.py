#!/usr/bin/env python3
"""Strict, offline command doubles for test_install.py; never use on a real PATH."""

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(os.environ["MANGOMAGIC_TEST_ROOT"]).resolve()
SCENARIO = json.loads((ROOT / "scenario.json").read_text())
STATE_FILE = ROOT / "state.json"
STATE = json.loads(STATE_FILE.read_text())
TOOL = Path(sys.argv[0]).name
ARGS = sys.argv[1:]
MODEL = "mangomagic/mangomagic-7.1"
EVENT = {"tool": TOOL, "args": ARGS}


def finish(status=0, stdout="", stderr=""):
    EVENT["status"] = status
    with (ROOT / "calls.jsonl").open("a") as log:
        log.write(json.dumps(EVENT) + "\n")
    STATE_FILE.write_text(json.dumps(STATE))
    if stdout:
        print(stdout, end="" if stdout.endswith("\n") else "\n")
    if stderr:
        print(stderr, file=sys.stderr)
    raise SystemExit(status)


def unexpected(reason):
    EVENT["unexpected"] = reason
    finish(97, stderr="UNEXPECTED MOCK CALL: " + reason)


def inside_root(value):
    path = Path(value).resolve()
    if path != ROOT and ROOT not in path.parents:
        unexpected("path escapes temporary test environment: " + str(path))
    return path


def drain_stdin():
    # Deliberately consume inherited input: this exposes installers that allow an
    # interactive CLI to eat the rest of a `curl ... | bash` program.
    EVENT["stdin_bytes"] = len(sys.stdin.buffer.read())


if TOOL == "uname":
    if ARGS in ([], ["-s"]):
        finish(stdout=SCENARIO.get("platform", "Darwin"))
    if ARGS == ["-m"]:
        finish(stdout="arm64")
    if ARGS == ["-r"]:
        finish(stdout="24.5.0")
    unexpected("uname arguments")

if TOOL == "sw_vers":
    finish(stdout="15.5")

if TOOL == "ollama":
    drain_stdin()
    if ARGS == ["--version"]:
        finish(stdout="ollama version is 0.34.1")
    if ARGS in (["list"], ["ps"]):
        finish(stdout="NAME    ID    SIZE    MODIFIED\n" + MODEL + "    fixture    1 GB    now")
    if "--help" in ARGS and ARGS[0] == "launch":
        finish(stdout="Usage: ollama launch chatgpt [--model MODEL] [--config] [--yes]")
    if ARGS == ["pull", MODEL]:
        EVENT["phase"] = "pull"
        if SCENARIO.get("pull_failure"):
            finish(41, "success\nMOCK_PULL_FAILURE", "simulated registry failure")
        finish(stdout="success")
    if ARGS and ARGS[0] == "launch":
        EVENT["phase"] = "registration"
        if ARGS != ["launch", "chatgpt", "--model", MODEL, "--config", "--yes"]:
            unexpected("registration must be config-only and noninteractive")
        if SCENARIO.get("registration_failure"):
            finish(42, "Ollama models added to ChatGPT.\nMOCK_REGISTRATION_FAILURE")
        if SCENARIO.get("registration_cancelled"):
            finish(stdout="Configuration cancelled.")
        finish(stdout="Ollama models added to ChatGPT.")
    if ARGS == ["run", MODEL, "--think=low", "--hidethinking", "Reply only READY"]:
        EVENT["phase"] = "inference"
        if SCENARIO.get("inference_failure"):
            finish(43, "READY", "MOCK_INFERENCE_FAILURE")
        if SCENARIO.get("inference_bad_reply"):
            finish(stdout="Unexpected reply")
        if SCENARIO.get("inference_extra_reply"):
            finish(stdout="READY. MangoMagic is available.")
        finish(stdout="READY")
    unexpected("ollama operation")

if TOOL == "curl":
    urls = [arg for arg in ARGS if arg.startswith(("http://", "https://"))]
    if len(urls) != 1:
        unexpected("curl requires exactly one known fixture URL")
    url = urls[0]
    if url in ("http://127.0.0.1:11434/api/version", "http://localhost:11434/api/version"):
        finish(stdout='{"version":"0.34.1"}')
    if url in ("http://127.0.0.1:11434/api/tags", "http://localhost:11434/api/tags"):
        finish(stdout=json.dumps({"models": [{"name": MODEL + ":latest", "model": MODEL + ":latest"}]}))
    if url.startswith("https://raw.githubusercontent.com/") and url.endswith(".js"):
        EVENT["phase"] = "helper_download"
        if SCENARIO.get("download_failure"):
            finish(22, stderr="MOCK_HELPER_DOWNLOAD_FAILURE")
        destinations = [ARGS[i + 1] for i, arg in enumerate(ARGS[:-1]) if arg in ("-o", "--output")]
        if len(destinations) != 1:
            unexpected("helper download must name a temporary output file")
        inside_root(destinations[0]).write_text("// Offline fixture: osascript itself is mocked.\n")
        finish()
    unexpected("network access is forbidden; no fixture for " + url)

if TOOL == "osascript":
    if "JavaScript" in ARGS:
        drain_stdin()
        operations = [arg for arg in ARGS if arg in ("check", "repair")]
        if len(ARGS) != 5 or ARGS[:2] != ["-l", "JavaScript"] or len(operations) != 1 or ARGS[-1] != MODEL:
            unexpected("metadata helper expects check MODEL or repair MODEL")
        helper = inside_root(ARGS[2])
        if not helper.is_file():
            unexpected("metadata helper was not downloaded into the temporary environment")
        operation = operations[0]
        EVENT["phase"] = "metadata_" + operation
        if operation == "check":
            wrapper_caps = SCENARIO.get("wrapper_caps", [])
            base_caps = SCENARIO.get("base_caps", ["vision", "thinking", "tools"])
            resolved = SCENARIO.get("base_resolved", True)
            EVENT.update(wrapper_caps=wrapper_caps, base_caps=base_caps, base_resolved=resolved)
            capabilities = wrapper_caps or (base_caps if resolved else [])
            if "vision" not in capabilities:
                finish(31, stderr="MOCK_CAPABILITY_FAILURE: vision could not be verified")
            finish(stdout="Verified capabilities: " + ", ".join(capabilities))
        if SCENARIO.get("repair_failure"):
            finish(32, stderr="MOCK_CATALOG_REPAIR_FAILURE")
        STATE["catalog_repaired"] = True
        finish(stdout="ChatGPT catalog verified.")
    if ARGS and ARGS[0] == "-":
        script = sys.stdin.read()
        EVENT["script"] = script
        if ARGS[1:] != [str(ROOT / "Applications" / "ChatGPT.app")]:
            unexpected("AppleScript must receive the exact discovered app path")
    else:
        script = "\n".join(ARGS)
    if not ARGS or (ARGS[0] != "-" and "com.openai.codex" not in script and '"ChatGPT"' not in script):
        unexpected("AppleScript must target the exact ChatGPT app")
    if "path to application" in script:
        EVENT["phase"] = "app_lookup"
        if SCENARIO.get("app_missing"):
            finish(1, stderr="MOCK_CHATGPT_MISSING")
        finish(stdout=str(ROOT / "Applications" / "ChatGPT.app"))
    if "quit" in script:
        EVENT["phase"] = "quit"
        if SCENARIO.get("quit_failure"):
            finish(1, stderr="MOCK_QUIT_FAILURE: user cancelled quitting")
        if not SCENARIO.get("quit_stuck"):
            STATE["running"] = False
        finish()
    if "running" in script or "exists process" in script:
        EVENT["phase"] = "running_check"
        finish(stdout="true" if STATE["running"] else "false")
    if "id of application" in script:
        finish(stdout="com.openai.codex")
    unexpected("AppleScript operation")

if TOOL == "pgrep":
    EVENT["phase"] = "running_check"
    if ARGS != ["-x", "ChatGPT"]:
        unexpected("process check must name ChatGPT exactly")
    finish(0 if STATE["running"] else 1, "424242" if STATE["running"] else "")

if TOOL == "open":
    EVENT["phase"] = "reopen"
    if ARGS != ["-a", str(ROOT / "Applications" / "ChatGPT.app")]:
        unexpected("open must target the exact ChatGPT app")
    if SCENARIO.get("open_failure"):
        finish(1, stderr="MOCK_REOPEN_FAILURE")
    STATE["running"] = not SCENARIO.get("open_stuck", False)
    finish()

if TOOL == "sleep":
    # Bounded polling loops progress instantly; no real sleeps or app operations.
    finish()

if TOOL == "mktemp":
    if "-d" in ARGS:
        result = tempfile.mkdtemp(prefix="work-", dir=ROOT / "tmp")
    else:
        fd, result = tempfile.mkstemp(prefix="work-", dir=ROOT / "tmp")
        os.close(fd)
    finish(stdout=result)

if TOOL == "rm":
    for arg in ARGS:
        if not arg.startswith("-"):
            path = inside_root(arg)
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
    finish()

if TOOL == "mkdir":
    for arg in ARGS:
        if not arg.startswith("-"):
            inside_root(arg).mkdir(parents="-p" in ARGS, exist_ok="-p" in ARGS)
    finish()

# These names are intentional traps, never proxies for host commands.
unexpected("forbidden or unimplemented external tool: " + TOOL)
