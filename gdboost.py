import gdb
import json
from openai import OpenAI


def frameContext():
    try:
        frame = gdb.selected_frame()
        if not frame:
            return {
                "error": "No frame is currently selected. Ensure the program is paused in a valid function."
            }

        block = frame.block()
        if not block:
            return {
                "frame_name": frame.name() or "No frame",
                "pc": hex(frame.pc()) if frame.pc() else "Unknown",
                "locals": {},
                "error": "Cannot locate block for frame. Frame context may be incomplete."
            }

        locals_context = {
            symbol.name: str(symbol.value(frame))
            for symbol in block if symbol.is_variable
        }

        return {
            "frame_name": frame.name() or "No frame",
            "pc": hex(frame.pc()) if frame.pc() else "Unknown",
            "locals": locals_context,
        }
    except Exception as e:
        return {
            "error": f"Error extracting frame context: {e}"
        }


def registerContext():
    registers = ["eax", "ecx", "edx", "ebx", "esp", "esi", "edi", "eip", 
                 "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rsp", "rbp", "rip"]
    register_context = {}
    for reg in registers:
        try:
            value = gdb.parse_and_eval(f"${reg}")
            if value is not None:
                register_context[reg] = str(value)
        except Exception:
            pass
    return register_context


def breakpointContext():
    try:
        return [
            {"location": bp.location, "enabled": bp.enabled}
            for bp in (gdb.breakpoints() or [])
        ]
    except Exception as e:
        print(f"Error extracting breakpoint context: {e}")
        return []


def disassemblyContext():
    try:
        return gdb.execute("disassemble", to_string=True)
    except gdb.error as e:
        print(f"Error extracting disassembly context: {e}")
        return "None"


def gdbContext():
    frame_context = frameContext() or {}
    return {
        "frame_name": frame_context.get("frame_name", "No frame"),
        "pc": frame_context.get("pc", "Unknown"),
        "locals": frame_context.get("locals", {}),
        "registers": registerContext(),
        "breakpoints": breakpointContext(),
        "disassembly": disassemblyContext(),
    }


class LLMCommand(gdb.Command):
    def __init__(self):
        super(LLMCommand, self).__init__("llm", gdb.COMMAND_USER)
        try:
            with open(".key", "r") as file:
                api_key = file.read().strip()
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            self.client = None

    def invoke(self, arg, from_tty):
        user_query = arg.strip()
        if not user_query:
            print("Error: No query provided. Usage: llm <your-query>")
            return

        if not self.client:
            print("Error: LLM client not initialized.")
            return

        context = gdbContext()

        base_prompt = """
        You are debugging an x86_64 binary. Here is the current state:
        - Current function: {frame_name}
        - Program counter (PC): {pc}
        - Local variables: {locals}
        - Registers: {registers}
        - Disassembly:
        {disassembly}
        - Breakpoints: {breakpoints}

        User query: {query}
        """

        try:
            full_prompt = base_prompt.format(
                frame_name=context["frame_name"],
                pc=context["pc"],
                locals=json.dumps(context["locals"], indent=2),
                registers=json.dumps(context["registers"], indent=2),
                disassembly=context["disassembly"],
                breakpoints=json.dumps(context["breakpoints"], indent=2),
                query=user_query,
            )

            completion = self.client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[{"role": "user", "content": full_prompt}],
            )

            response = completion.choices[0].message.content
            print(f"{response}")
        except Exception as e:
            print(f"Error querying LLM: {e}")


LLMCommand()
