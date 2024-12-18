import gdb
from gdbContext import *
from langchain.llms import Ollama # type: ignore
from langchain.prompts import PromptTemplate # type: ignore
from langchain.chains import LLMChain # type: ignore

class LLMCommand(gdb.Command):
    def __init__(self):
        super(LLMCommand, self).__init__("llm", gdb.COMMAND_USER)
        self.llm = Ollama(model="llama3.1")

    def invoke(self, arg, from_tty):
        context = gdbContext()
        prompt_template = """
        You are debugging an x86_64 binary. Here is the current state:
        - Current function: {frame_name}
        - Program counter (PC): {pc}
        - Local variables: {locals}
        - Registers: {registers}
        - Disassembly:
        {disassembly}
        - Breakpoints: {breakpoints}

        User query: {query}

        Provide a helpful and concise response based on this context.
        """
        prompt = PromptTemplate(
            input_variables=["frame_name", "pc", "locals", "registers", "disassembly", "breakpoints", "query"],
            template=prompt_template
        )

        llm_chain = LLMChain(llm=self.llm, prompt=prompt)

        input_context = {
            "frame_name": context["frame_name"],
            "pc": context["pc"],
            "locals": context["locals"],
            "registers": context["registers"],
            "disassembly": context["disassembly"],
            "breakpoints": context["breakpoints"],
            "query": arg
        }

        try:
            response = llm_chain.run(input_context)
            print(f"LLM Response:\n{response}")
        except Exception as e:
            print(f"Error querying LLM: {e}")

LLMCommand()
