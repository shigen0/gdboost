import gdb

def frameContext():
    context = {
        "frame_name": "No frame",
        "pc": "Unknown",
        "locals": {}
    }
    
    frame = gdb.selected_frame()
    if frame:
        context["frame_name"] = frame.name()
        context["pc"] = frame.pc()
        context["locals"] = {
            symbol.name: str(symbol.value(frame))
            for symbol in frame.block() if symbol.is_variable
        }
    else:
        context = None
    return context

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
    return [
        {"location": bp.location, "enabled": bp.enabled}
        for bp in gdb.breakpoints() or []
    ]

def disassemblyContext():
    try:
        return gdb.execute("disassemble", to_string=True)
    except gdb.error:
        return None

def gdbContext():
    context = {}
    
    context.update(frameContext)
    context["registers"] = registerContext()
    context["breakpoints"] = breakpointContext()
    context["disassembly"] = disassemblyContext()
    
    return context