#!/bin/bash

# shellcheck source=/dev/null

declare current_dir && \
    current_dir="$(dirname "${BASH_SOURCE[0]}")" && \
    cd "${current_dir}" && \
    source "$HOME/set-me-up/dotfiles/utilities/import.sh"

smu::import base

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

main() {

    ask_for_sudo

	sudo pacman -Syu --noconfirm \
			&& sudo pacman -Sc --noconfirm

}

main
