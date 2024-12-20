import gdb
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate  # Updated import
from langchain.chains import LLMChain  # Updated import


def frameContext():
    try:
        frame = gdb.selected_frame()
        if not frame:
            return None

        block = frame.block()
        if not block:
            return {
                "frame_name": frame.name() or "No frame",
                "pc": hex(frame.pc()) if frame.pc() else "Unknown",
                "locals": {}
            }

        context = {
            "frame_name": frame.name() or "No frame",
            "pc": hex(frame.pc()) if frame.pc() else "Unknown",
            "locals": {
                symbol.name: str(symbol.value(frame))
                for symbol in block if symbol.is_variable
            }
        }
        return context
    except Exception as e:
        print(f"Error extracting frame context: {e}")
        return None


def registerContext():
    registers = ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rsp", "rbp", "rip"]
    register_context = {}

    for reg in registers:
        try:
            register_context[reg] = str(gdb.parse_and_eval(f"${reg}"))
        except gdb.error:
            register_context[reg] = None

    return register_context


def breakpointContext():
    try:
        return [
            {"location": bp.location, "enabled": bp.enabled}
            for bp in gdb.breakpoints() or []
        ]
    except Exception as e:
        print(f"Error extracting breakpoint context: {e}")
        return []


def disassemblyContext():
    try:
        return gdb.execute("disassemble", to_string=True)
    except gdb.error as e:
        print(f"Error extracting disassembly context: {e}")
        return None


def gdbContext():
    frame_context = frameContext()
    return {
        "frame_name": frame_context["frame_name"] if frame_context else "No frame",
        "pc": frame_context["pc"] if frame_context else "Unknown",
        "locals": frame_context["locals"] if frame_context else {},
        "registers": registerContext(),
        "breakpoints": breakpointContext(),
        "disassembly": disassemblyContext(),
    }


class LLMCommand(gdb.Command):
    def __init__(self):
        super(LLMCommand, self).__init__("llm", gdb.COMMAND_USER)
        self.llm = OllamaLLM(model="llama2-uncensored")

    def invoke(self, arg, from_tty):
        user_query = arg.strip()
        if not user_query:
            print("Error: No query provided. Usage: llm <your-query>")
            return

        # Generate debugging context
        context = gdbContext()

        # Simplified prompt template
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

        # Input to the LLM
        input_context = {
            "frame_name": context.get("frame_name", "No frame"),
            "pc": context.get("pc", "Unknown"),
            "locals": context.get("locals", {}),
            "registers": context.get("registers", {}),
            "disassembly": context.get("disassembly", "None"),
            "breakpoints": context.get("breakpoints", []),
            "query": user_query,
        }

        try:
            # Format the full prompt
            full_prompt = base_prompt.format(
                frame_name=input_context["frame_name"],
                pc=input_context["pc"],
                locals=input_context["locals"],
                registers=input_context["registers"],
                disassembly=input_context["disassembly"],
                breakpoints=input_context["breakpoints"],
                query=input_context["query"]
            )

            response = self.llm(full_prompt)
            print(f"LLM Response:\n{response}")
        except Exception as e:
            print(f"Error querying LLM: {e}")


LLMCommand()
