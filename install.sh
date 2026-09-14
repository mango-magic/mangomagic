#!/bin/bash
# MangoMagic 7.1 - ManyMangoes' macOS installer. Requires only stock Bash 3.2.
# Download completely before executing (also propagates a failed download):
# /bin/bash -c 'installer=$(curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/install.sh) && /bin/bash -c "$installer"'
# Piped input is also supported: curl -fsSL URL | /bin/bash -s -- --no-restart
# Ship configure-chatgpt.js beside this file and at the same GitHub base URL.

# All work is inside main: an incomplete function cannot execute a partial install.
main() {
    set -euo pipefail

    MODEL='mangomagic/mangomagic-7.1'
    RELEASE_URL='https://raw.githubusercontent.com/mango-magic/mangomagic/main'
    INSTALLER_VERSION='2026.09.14.2'
    CHATGPT_BUNDLE_ID='com.openai.codex'
    RESTART_CHATGPT=1
    WORK_DIR=''
    STAGE='preflight'
    OLLAMA_BIN=''
    OLLAMA_APP=''
    CHATGPT_APP=''
    APP_RUNNING=''
    HELPER=''
    RESET='' BOLD='' ITALIC='' GOLD='' CREAM='' SAND='' NAVY_BG='' PAPER=''

    usage() {
        cat <<'USAGE'
MangoMagic 7.1. By ManyMangoes.

Usage: /bin/bash install.sh [--no-restart]
       curl -fsSL URL | /bin/bash -s -- [--no-restart]

  --no-restart  Configure and verify the model; leave ChatGPT running as it is.
  --help       Show this help without changing anything.

By default, ChatGPT is asked to quit gracefully, then reopened and checked.
Use --no-restart when running inside ChatGPT itself.
Ollama account sign-in, when required, uses Ollama's normal authentication.
USAGE
    }

    fail() {
        printf '\n  %sStopped.%s %s\n' "$BOLD" "$RESET" "$1" >&2
        exit "${2:-1}"
    }

    finish() {
        local status=$?
        trap - EXIT INT TERM
        if [ "$status" -ne 0 ]; then
            printf '  Installation incomplete during %s (exit %s).\n' "$STAGE" "$status" >&2
        fi
        if [ -n "$WORK_DIR" ]; then
            # Only our mktemp directory. Cleanup cannot turn a failed install into success.
            if ! rm -rf -- "$WORK_DIR"; then
                printf '  Could not remove temporary files: %s\n' "$WORK_DIR" >&2
            fi
        fi
        printf '%s' "$RESET"
        exit "$status"
    }

    note() { printf '       %s\n' "$1"; }

    step() {
        STAGE=$2
        printf '\n  %s%s[%s/6]%s %s%s.%s\n' "$GOLD" "$BOLD" "$1" "$RESET" "$BOLD" "$2" "$RESET"
    }

    rule() {
        printf '  %s------------------------------------------------------%s\n' "$SAND" "$RESET"
    }

    banner() {
        # The terminal keeps its own font. Use the exact five-colour brand palette,
        # with bounded panels rather than changing the customer's terminal theme.
        if [ -t 1 ] && [ "${TERM:-dumb}" != 'dumb' ] && [ -z "${NO_COLOR+x}" ]; then
            RESET=$'\033[0m'
            BOLD=$'\033[1m'
            ITALIC=$'\033[3m'
            GOLD=$'\033[38;2;241;171;28m'
            CREAM=$'\033[38;2;246;240;226m'
            SAND=$'\033[38;2;201;185;138m'
            NAVY_BG=$'\033[48;2;17;21;39m'
            PAPER=$'\033[48;2;246;240;226m\033[38;2;26;26;26m'
        fi
        printf '\n'
        printf '  %s%s| %s%-52s%s\n' "$NAVY_BG" "$GOLD" "$BOLD" 'M A N Y M A N G O E S' "$RESET"
        printf '  %s%s| %s%s%-52s%s\n' "$NAVY_BG" "$GOLD" "$CREAM" "$BOLD" 'MangoMagic 7.1.' "$RESET"
        printf '  %s%s| %s%-52s%s\n' "$NAVY_BG" "$GOLD" "$CREAM" 'The business AI system for the modern worker.' "$RESET"
        printf '  %s%s  %-52s%s\n' "$PAPER" "$ITALIC" 'Concise answers. Checked work. Useful agents.' "$RESET"
        printf '\n'
        note "$MODEL"
        if [ "$RESTART_CHATGPT" -eq 1 ]; then
            note 'ChatGPT will quit gracefully and reopen after setup.'
        else
            note 'ChatGPT restart is deferred (--no-restart).'
        fi
    }

    download() {
        local url=$1 destination=$2
        if curl --fail --show-error --silent --location \
            --proto '=https' --proto-redir '=https' --tlsv1.2 \
            --connect-timeout 15 --max-time 120 --retry 2 \
            --output "$destination" "$url"; then
            [ -s "$destination" ] || fail "The download was empty: $url"
        else
            fail "Download failed: $url. Check your connection and rerun." "$?"
        fi
    }

    load_helper() {
        local source_file=${BASH_SOURCE[0]:-} source_dir=''
        if [ -n "$source_file" ] && [ -f "$source_file" ]; then
            case "$source_file" in
                */*) source_dir=${source_file%/*} ;;
                *) source_dir='.' ;;
            esac
            source_dir=$(cd -- "$source_dir" && pwd -P)
            if [ -r "$source_dir/configure-chatgpt.js" ] && [ -s "$source_dir/configure-chatgpt.js" ]; then
                HELPER="$source_dir/configure-chatgpt.js"
                return 0
            fi
        fi
        HELPER="$WORK_DIR/configure-chatgpt.js"
        download "$RELEASE_URL/configure-chatgpt.js?v=$INSTALLER_VERSION" "$HELPER"
    }

    find_ollama() {
        local candidate=''
        if candidate=$(command -v ollama 2>/dev/null) && [ -x "$candidate" ]; then
            OLLAMA_BIN=$candidate
            return 0
        fi
        # The macOS app may be installed even when its CLI symlink is absent.
        for candidate in "/Applications/Ollama.app/Contents/Resources/ollama" \
            "$HOME/Applications/Ollama.app/Contents/Resources/ollama"; do
            if [ -x "$candidate" ]; then
                OLLAMA_BIN=$candidate
                return 0
            fi
        done
        return 1
    }

    ollama_responds() {
        curl --fail --silent --show-error --noproxy '*' \
            --connect-timeout 2 --max-time 2 \
            "$OLLAMA_HOST/api/version" >"$WORK_DIR/ollama-health.json" 2>"$WORK_DIR/ollama-health.error"
    }

    prepare_ollama() {
        local version_output='' version='' launch_help='' candidate='' deadline=0 command_status=0
        if ! find_ollama; then
            if [ -d '/Applications/Ollama.app' ] || [ -d "$HOME/Applications/Ollama.app" ]; then
                fail 'Ollama.app exists but its CLI is missing. Reinstall from https://ollama.com/download/mac and rerun.'
            fi
            note 'Installing Ollama using its official macOS installer.'
            note 'macOS may request your password to install the Ollama CLI.'
            # Official install.sh was checked against its Darwin branch (2026-09-14).
            # Download first: a failed curl must never execute a partial installer.
            download 'https://ollama.com/install.sh' "$WORK_DIR/install-ollama.sh"
            if sh "$WORK_DIR/install-ollama.sh"; then
                hash -r
            else
                fail 'The official Ollama installer failed. Resolve its error above and rerun.' "$?"
            fi
            find_ollama || fail 'Ollama installation finished without a usable CLI. Open Ollama, complete setup, then rerun.'
        fi

        if version_output=$("$OLLAMA_BIN" --version 2>&1); then
            # Offline clients print "Warning: client version is ..."; if the server
            # differs, this final client-version line also takes precedence.
            version=$(printf '%s\n' "$version_output" | awk '/^(ollama version is |Warning: client version is )/ { value=$NF } END { print value }')
        else
            command_status=$?
            printf '%s\n' "$version_output" >&2
            fail 'Could not read the Ollama version.' "$command_status"
        fi
        # 0.34.0 is the verified native ChatGPT integration: its --config path
        # returns before Run, so --yes cannot secretly restart the host app.
        if ! awk -v version="$version" 'BEGIN {
            sub(/^v/, "", version)
            if (version !~ /^[0-9]+\.[0-9]+\.[0-9]+([-+].*)?$/) exit 1
            split(version, v, ".")
            exit !(v[1]+0 > 0 || (v[1]+0 == 0 && v[2]+0 >= 34))
        }'; then
            fail 'Ollama 0.34.0 or newer is required. Update from https://ollama.com/download/mac and rerun.'
        fi
        if launch_help=$("$OLLAMA_BIN" launch --help 2>&1); then
            case "$launch_help" in *chatgpt*) ;; *) fail 'This Ollama build does not support native ChatGPT registration. Update Ollama and rerun.' ;; esac
            case "$launch_help" in *--config*) ;; *) fail 'Ollama is missing the configure-only option. Update Ollama and rerun.' ;; esac
            case "$launch_help" in *--yes*) ;; *) fail 'Ollama is missing noninteractive registration support. Update Ollama and rerun.' ;; esac
        else
            command_status=$?
            printf '%s\n' "$launch_help" >&2
            fail 'Could not inspect native Ollama ChatGPT support.' "$command_status"
        fi

        if ! ollama_responds; then
            case "$OLLAMA_BIN" in
                */Ollama.app/Contents/Resources/ollama) OLLAMA_APP=${OLLAMA_BIN%/Contents/Resources/ollama} ;;
            esac
            if [ -z "$OLLAMA_APP" ]; then
                for candidate in '/Applications/Ollama.app' "$HOME/Applications/Ollama.app"; do
                    if [ -d "$candidate" ]; then OLLAMA_APP=$candidate; break; fi
                done
            fi
            [ -n "$OLLAMA_APP" ] || fail 'Ollama is installed but its server is stopped. Run "ollama serve" in another Terminal, then rerun.'
            note 'Starting Ollama. Waiting up to 30 seconds for its local API.'
            if open -g -a "$OLLAMA_APP" --args hidden; then
                deadline=$((SECONDS + 30))
            else
                fail 'macOS could not open Ollama. Open it manually and finish its setup, then rerun.' "$?"
            fi
            while ! ollama_responds; do
                if [ "$SECONDS" -ge "$deadline" ]; then
                    cat "$WORK_DIR/ollama-health.error" >&2
                    fail 'Ollama did not respond within 30 seconds. Open Ollama, finish any setup prompts, then rerun.'
                fi
                sleep 1
            done
        fi
        note "Ollama $version is available; its local API is responding."
    }

    read_app_state() {
        if APP_RUNNING=$(osascript - "$CHATGPT_APP" <<'APPLESCRIPT'
on run argv
    set targetApp to item 1 of argv
    with timeout of 5 seconds
        return application targetApp is running
    end timeout
end run
APPLESCRIPT
        ); then
            case "$APP_RUNNING" in true|false) ;; *) fail 'macOS returned an unknown ChatGPT running state.' ;; esac
        else
            fail 'Could not verify whether ChatGPT is running.' "$?"
        fi
    }

    wait_for_app_state() {
        local wanted=$1 deadline=$((SECONDS + $2))
        while :; do
            read_app_state
            [ "$APP_RUNNING" = "$wanted" ] && return 0
            [ "$SECONDS" -lt "$deadline" ] || return 1
            sleep 1 || fail 'The ChatGPT state check was interrupted.'
        done
    }

    restart_chatgpt() {
        read_app_state
        if [ "$APP_RUNNING" = 'true' ]; then
            note 'Asking ChatGPT to quit. Complete any save prompt in the app.'
            # Exact app path, passed as data. Never terminate matching processes.
            if osascript - "$CHATGPT_APP" <<'APPLESCRIPT'
on run argv
    set targetApp to item 1 of argv
    with timeout of 15 seconds
        if application targetApp is running then
            tell application targetApp to quit
        end if
    end timeout
end run
APPLESCRIPT
            then
                if ! wait_for_app_state false 30; then
                    fail 'ChatGPT did not quit within 30 seconds. Finish any save prompt, quit it yourself, then reopen it.'
                fi
            else
                fail 'ChatGPT declined or could not complete the quit request. Quit and reopen it yourself to load the model.' "$?"
            fi
        fi
        if open -a "$CHATGPT_APP"; then
            if ! wait_for_app_state true 30; then
                fail 'ChatGPT did not start within 30 seconds. Open it manually to load the configured model.'
            fi
        else
            fail 'macOS could not reopen ChatGPT. Open it manually to load the configured model.' "$?"
        fi
        # Catch an immediate launch-and-crash instead of trusting open's exit code.
        sleep 2
        read_app_state
        [ "$APP_RUNNING" = 'true' ] || fail 'ChatGPT opened but exited again. Open it manually and check the app.'
        note 'ChatGPT is running with the updated model configuration.'
    }

    while [ "$#" -gt 0 ]; do
        case "$1" in
            --no-restart) RESTART_CHATGPT=0 ;;
            --help|-h) usage; return 0 ;;
            --) shift; [ "$#" -eq 0 ] || fail 'Unexpected positional arguments. Use --help for usage.' 2; break ;;
            *) fail "Unknown option: $1. Use --help for usage." 2 ;;
        esac
        shift
    done

    trap finish EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    banner
    step 1 'Check this Mac'
    [ "$(uname -s)" = 'Darwin' ] || fail 'This installer supports macOS only.'
    [ "$EUID" -ne 0 ] || fail 'Run this installer in your own macOS login, without sudo.'
    local macos_version='' tool=''
    for tool in curl osascript open awk mktemp rm sh sleep sw_vers; do
        command -v "$tool" >/dev/null 2>&1 || fail "Required macOS tool is missing: $tool"
    done
    macos_version=$(sw_vers -productVersion)
    case "${macos_version%%.*}" in ''|*[!0-9]*) fail 'Could not determine the macOS version.' ;; esac
    [ "${macos_version%%.*}" -ge 14 ] || fail 'Ollama requires macOS Sonoma 14 or newer. Update macOS and rerun.'
    # The native desktop integration and helper must use the same local daemon.
    case "${OLLAMA_HOST:-}" in
        ''|127.0.0.1:11434|localhost:11434|http://127.0.0.1:11434|http://localhost:11434|http://127.0.0.1:11434/|http://localhost:11434/) ;;
        *) fail 'This desktop installer needs local Ollama on port 11434. Unset OLLAMA_HOST in this Terminal and rerun.' ;;
    esac
    export OLLAMA_HOST='http://127.0.0.1:11434'
    if CHATGPT_APP=$(osascript -e 'with timeout of 5 seconds' \
        -e "return POSIX path of (path to application id \"$CHATGPT_BUNDLE_ID\")" \
        -e 'end timeout'); then
        CHATGPT_APP=${CHATGPT_APP%/}
        case "$CHATGPT_APP" in /*.app) ;; *) fail 'macOS did not resolve a valid ChatGPT application path.' ;; esac
        [ -d "$CHATGPT_APP" ] || fail 'The ChatGPT application is missing. Install it from https://chatgpt.com/download and rerun.'
    else
        fail 'Install the current ChatGPT Mac app from https://chatgpt.com/download, open it once, then rerun.' "$?"
    fi
    note "Found $CHATGPT_APP"
    WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/mangomagic-install.XXXXXXXX")
    load_helper

    step 2 'Prepare Ollama'
    prepare_ollama

    step 3 'Download MangoMagic 7.1'
    if "$OLLAMA_BIN" pull "$MODEL"; then
        note 'Model download completed.'
    else
        fail 'Ollama could not pull the model. Resolve the error above (use "ollama signin" if requested), then rerun.' "$?"
    fi

    step 4 'Verify model capabilities'
    # The helper resolves the live declared remote base when wrapper metadata is
    # absent. Never infer capabilities from the model name or hardcode a base.
    if osascript -l JavaScript "$HELPER" check "$MODEL"; then
        note 'Verified vision, tools and thinking from live model metadata.'
    else
        fail 'Model capability verification failed. Resolve the helper error above before continuing.' "$?"
    fi

    # Metadata alone cannot confirm this customer's Ollama cloud entitlement.
    # One short response verifies inference, including the advertised Low setting.
    note 'Checking Ollama cloud access with one short test response.'
    # A language model can answer correctly without repeating a magic word.
    # Validate a completed API response, not the wording of its answer.
    if osascript -l JavaScript "$HELPER" smoke "$MODEL"; then
        note 'Ollama cloud access and a Low-thinking response are verified.'
    else
        fail 'Ollama could not run the model. Use "ollama signin" if authentication is requested; resolve any cloud access or usage-limit error, then rerun.' "$?"
    fi

    step 5 'Connect MangoMagic to ChatGPT'
    local registration_output='' registration_status=0
    # --config prevents native launch; --yes handles configuration confirmation.
    # No auth files are read or rewritten here. Authentication stays with Ollama.
    if registration_output=$("$OLLAMA_BIN" launch chatgpt --model "$MODEL" --config --yes 2>&1); then
        printf '%s\n' "$registration_output"
    else
        registration_status=$?
        printf '%s\n' "$registration_output" >&2
        fail 'Native Ollama registration failed. Resolve its error above, then rerun.' "$registration_status"
    fi
    # Ollama can return zero for cancellation. Require its documented completion
    # message as well as a successful exit, then independently validate the catalog.
    case "$registration_output" in
        *'Ollama models added to ChatGPT.'*) ;;
        *) fail 'Ollama did not confirm ChatGPT registration. Update Ollama or complete its setup, then rerun.' ;;
    esac
    if osascript -l JavaScript "$HELPER" repair "$MODEL"; then
        note 'MangoMagic 7.1 is registered with verified model capabilities.'
    else
        fail 'ChatGPT catalog verification or repair failed. Resolve the helper error above, then rerun.' "$?"
    fi

    if [ "$RESTART_CHATGPT" -eq 1 ]; then
        step 6 'Reopen ChatGPT'
        restart_chatgpt
    else
        step 6 'Defer ChatGPT restart'
        note 'Configuration is complete. Restart ChatGPT to load its updated model list.'
    fi

    printf '\n'
    rule
    if [ "$RESTART_CHATGPT" -eq 1 ]; then
        printf '\n  %s%sMangoMagic 7.1 is ready.%s\n' "$GOLD" "$BOLD" "$RESET"
    else
        printf '\n  %s%sMangoMagic 7.1 is configured.%s\n' "$GOLD" "$BOLD" "$RESET"
        note 'ChatGPT restart is still pending (--no-restart).'
    fi
    printf '\n  In ChatGPT, open the model selector and choose:\n'
    printf '  %sMangoMagic 7.1%s (%s)\n' "$BOLD" "$RESET" "$MODEL"
    printf '\n  Try: "Turn these notes into a clear action plan.\n'
    printf '        Check the facts and keep it concise."\n\n'
    rule
    printf '  %sM A N Y M A N G O E S%s  -  Less busywork. More useful work.\n\n' "$GOLD" "$RESET"
}

# Children must never consume the curl stream containing this program. Explicit
# arguments + --yes keep configuration noninteractive; sudo can use /dev/tty.
main "$@" </dev/null
