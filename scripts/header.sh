#!/bin/bash

# shellcheck source=/dev/null
source /dev/stdin <<<"$(curl -s "https://raw.githubusercontent.com/smeltery/utilities/v1.2.0/import.sh")"

smu::import base

# shellcheck source=/dev/null
source "$(dirname "${BASH_SOURCE[0]}")/lib/output.sh"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

header() {
    echo -en "\n███████╗███████╗████████╗   ███╗   ███╗███████╗    ██╗   ██╗██████╗"
    echo -en "\n██╔════╝██╔════╝╚══██╔══╝   ████╗ ████║██╔════╝    ██║   ██║██╔══██╗"
    echo -en "\n███████╗█████╗     ██║█████╗██╔████╔██║█████╗█████╗██║   ██║██████╔╝"
    echo -en "\n╚════██║██╔══╝     ██║╚════╝██║╚██╔╝██║██╔══╝╚════╝██║   ██║██╔═══╝"
    echo -en "\n███████║███████╗   ██║      ██║ ╚═╝ ██║███████╗    ╚██████╔╝██║"
    echo -en "\n╚══════╝╚══════╝   ╚═╝      ╚═╝     ╚═╝╚══════╝     ╚═════╝ ╚═╝"
    echo -en "\n\n"
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# shellcheck disable=SC2154
output_ohai "Installing set-me-up"

echo -e "For more information, please see [https://github.com/smeltery/set-me-up-docs]."
echo -e "Please follow the on-screen instructions.\n"

output_opoo "This script sets up new machines, *use with caution*."
output_opoo "Ensure your Mac, *Debian*, or *Arch* Linux system is fully up-to-date."

header
