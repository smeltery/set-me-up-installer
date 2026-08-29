"""Homebrew-compatible CLI output helpers for set-me-up."""

import os
import sys

BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"


def tty_colour_enabled(stream=None):
    stream = stream or sys.stderr
    return (
        stream.isatty()
        and not os.environ.get("NO_COLOR")
        and not os.environ.get("SMU_NO_COLOR")
        and not os.environ.get("DOTFILES_NO_COLOR")
    )


def emoji_enabled():
    return not any(
        os.environ.get(key)
        for key in ("HOMEBREW_NO_EMOJI", "SMU_NO_EMOJI", "DOTFILES_NO_EMOJI")
    )


def ohai(message, file=None):
    file = file or sys.stderr
    if tty_colour_enabled(file):
        print(f"{BLUE}==>{RESET} {BOLD}{message}{RESET}", file=file)
    else:
        print(f"==> {message}", file=file)


def opoo(message, file=None):
    file = file or sys.stderr
    if tty_colour_enabled(file):
        print(f"{YELLOW}Warning:{RESET} {message}", file=file)
    else:
        print(f"Warning: {message}", file=file)


def onoe(message, file=None):
    file = file or sys.stderr
    if tty_colour_enabled(file):
        print(f"{RED}Error:{RESET} {message}", file=file)
    else:
        print(f"Error: {message}", file=file)


def pretty_ok(message, file=None):
    file = file or sys.stderr
    if not sys.stdout.isatty() and not sys.stderr.isatty():
        print(message, file=file)
        return
    if not emoji_enabled():
        if tty_colour_enabled(file):
            print(f"{GREEN}{BOLD}{message} (ok){RESET}", file=file)
        else:
            print(f"{message} (ok)", file=file)
    elif tty_colour_enabled(file):
        print(f"{BOLD}{message} {GREEN}✔{RESET}", file=file)
    else:
        print(f"{message} ✔", file=file)


def pretty_warn(message, file=None):
    file = file or sys.stderr
    if not sys.stdout.isatty() and not sys.stderr.isatty():
        print(message, file=file)
        return
    if not emoji_enabled():
        if tty_colour_enabled(file):
            print(f"{YELLOW}{BOLD}{message} (warning){RESET}", file=file)
        else:
            print(f"{message} (warning)", file=file)
    elif tty_colour_enabled(file):
        print(f"{BOLD}{message} {YELLOW}⚠{RESET}", file=file)
    else:
        print(f"{message} ⚠", file=file)


def pretty_duration(seconds):
    seconds = int(seconds)
    hide_seconds = seconds > 300
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        if not hide_seconds and seconds:
            return f"{minutes}m {seconds}s"
        return f"{minutes}m"
    return f"{seconds}s"


def install_badge():
    return (
        os.environ.get("SMU_INSTALL_BADGE")
        or os.environ.get("HOMEBREW_INSTALL_BADGE")
        or "🍺"
    )


def print_repo_update_status(name, status, dirty=False, file=None):
    suffix = " (dirty working tree)" if dirty else ""
    label = f"{name}: {status}{suffix}"
    if status in ("blocked", "failed") or dirty:
        pretty_warn(label, file=file)
    elif status in ("current", "updated", "reset"):
        pretty_ok(label, file=file)
    else:
        print(f"    {label}", file=file or sys.stderr)
