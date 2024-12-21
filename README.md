# GDBoost

Reverse x86 binaries with GDB LLM boosted ⚡

## Setup

`git clone https://github.com/shigen0/gdboost`  
`sudo ./setup.sh --key YOUR_OPENROUTER_KEY`

## Usage

Launch gdb with your x86 64 binary and start talking with the LLM asking for example : `(gdb) llm Hey ! Can you give me the value of eax register please ?`.  
Of course you should at least run the binary if you wanna see the information below.

## How it works

This script retrieves debugging information from GDB and sends it to the LLM to assist with answering user queries during debugging. Below are the key details sent:

    Frame Context:
        Current function name.
        Program counter (PC) address.
        Local variables and their values.

    Register Context:
        Values of key registers (e.g., rax, rbx, rip for x64, eax, ebx, eip for x86).

    Breakpoint Context:
        Active breakpoints with location and enabled/disabled status.

    Disassembly Context:
        Assembly instructions for the current function or code segment.

    User Query:
        The query provided by the user, directing the LLM to focus on specific issues.

    Error Handling:
        Any missing or inaccessible data is replaced with error messages for LLM context.

## Notes

- Will update the robustness of the code for handling cases and errors, that's a first version ;)
- There may be an inconsistency between your python version and gdb python version, you should fix it manually
