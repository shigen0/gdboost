#!/bin/bash

KEY_FILE=".key"
GDBINIT_FILE="$HOME/.gdbinit"
GDB_SCRIPT="gdboost.py"
CURRENT_DIR=$(pwd)

add_to_gdbinit() {
    echo "Updating $GDBINIT_FILE..."
    if [[ ! -s "$GDBINIT_FILE" ]]; then
        echo "$GDBINIT_CONTENT" > "$GDBINIT_FILE"
    else
        echo -e "\n\n$GDBINIT_CONTENT" >> "$GDBINIT_FILE"
    fi
}

GDBINIT_CONTENT=$(cat <<EOF
define llm
set disassembly-flavor intel
set debuginfod enabled on
unset env LINES
unset env COLUMNS
source $CURRENT_DIR/$GDB_SCRIPT
end
EOF
)

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 --key <openrouter_key>"
    exit 1
fi

if [[ "$1" == "--key" && -n "$2" ]]; then
    echo "Saving OpenRouter key to $KEY_FILE..."
    echo "$2" > "$KEY_FILE"
    echo "Key saved."
else
    echo "Invalid arguments. Usage: $0 --key <openrouter_key>"
    exit 1
fi

add_to_gdbinit

echo "Setup complete! You can now launch gdb with your x86 binary and discuss with the LLM by typing `(gdb) llm here is your prompt`"