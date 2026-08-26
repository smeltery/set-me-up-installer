#!/usr/bin/env bash
#
# Brew-compatible CLI output helpers for set-me-up.
# Conventions mirror Homebrew's Library/Homebrew/utils.sh and
# Library/Homebrew/utils/output.rb.
#
# shellcheck shell=bash

output_tty_colour_enabled() {
  local stream="${1:-2}"
  [[ -t "$stream" ]] &&
    [[ -z "${NO_COLOR:-}" ]] &&
    [[ -z "${SMU_NO_COLOR:-}" ]] &&
    [[ -z "${DOTFILES_NO_COLOR:-}" ]]
}

output_emoji_enabled() {
  [[ -z "${HOMEBREW_NO_EMOJI:-}" ]] &&
    [[ -z "${SMU_NO_EMOJI:-}" ]] &&
    [[ -z "${DOTFILES_NO_EMOJI:-}" ]]
}

output_ohai() {
  if output_tty_colour_enabled 2; then
    printf '\033[34m==>\033[0m \033[1m%s\033[0m\n' "$*" >&2
  else
    printf '==> %s\n' "$*" >&2
  fi
}

output_opoo() {
  if output_tty_colour_enabled 2; then
    printf '\033[33mWarning:\033[0m %s\n' "$*" >&2
  else
    printf 'Warning: %s\n' "$*" >&2
  fi
}

output_onoe() {
  if output_tty_colour_enabled 2; then
    printf '\033[31mError:\033[0m %s\n' "$*" >&2
  else
    printf 'Error: %s\n' "$*" >&2
  fi
}

output_indent() {
  sed 's/^/    /' >&2
}

output_pretty_ok() {
  local string="$1"
  if [[ ! -t 1 && ! -t 2 ]]; then
    printf '%s\n' "$string"
    return
  fi
  if ! output_emoji_enabled; then
    if output_tty_colour_enabled 2; then
      printf '\033[32m\033[1m%s (ok)\033[0m\n' "$string" >&2
    else
      printf '%s (ok)\n' "$string" >&2
    fi
  elif output_tty_colour_enabled 2; then
    printf '\033[1m%s \033[32m✔\033[0m\n' "$string" >&2
  else
    printf '%s ✔\n' "$string" >&2
  fi
}

output_pretty_warn() {
  local string="$1"
  if [[ ! -t 1 && ! -t 2 ]]; then
    printf '%s\n' "$string"
    return
  fi
  if ! output_emoji_enabled; then
    if output_tty_colour_enabled 2; then
      printf '\033[33m\033[1m%s (warning)\033[0m\n' "$string" >&2
    else
      printf '%s (warning)\n' "$string" >&2
    fi
  elif output_tty_colour_enabled 2; then
    printf '\033[1m%s \033[33m⚠\033[0m\n' "$string" >&2
  else
    printf '%s ⚠\n' "$string" >&2
  fi
}

output_pretty_duration() {
  local seconds="${1:-0}"
  seconds="${seconds%%.*}"
  local hide_seconds=0 minutes hours
  ((seconds > 300)) && hide_seconds=1
  minutes=$((seconds / 60))
  seconds=$((seconds % 60))
  hours=$((minutes / 60))
  minutes=$((minutes % 60))

  if ((hours > 0)); then
    printf '%dh %dm' "$hours" "$minutes"
  elif ((minutes > 0)); then
    if ((hide_seconds == 0 && seconds > 0)); then
      printf '%dm %ds' "$minutes" "$seconds"
    else
      printf '%dm' "$minutes"
    fi
  else
    printf '%ds' "$seconds"
  fi
}

output_install_badge() {
  printf '%s' "${SMU_INSTALL_BADGE:-${HOMEBREW_INSTALL_BADGE:-🍺}}"
}
