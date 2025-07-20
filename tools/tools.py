import re
from typing import Callable, Dict, Any, List

# Tool registry
_TOOL_REGISTRY = []

def function_tool(func: Callable = None, *, name: str = None, description: str = None, parameters: Dict[str, Any] = None):
    """
    Decorator to register a function as a tool and auto-generate its OpenAI function schema.
    """
    def decorator(f):
        tool_name = name or f.__name__
        tool_description = description or (f.__doc__.strip() if f.__doc__ else "")
        if parameters is None:
            import inspect
            sig = inspect.signature(f)
            props = {}
            required = []
            # Map Python types to OpenAI types
            type_map = {
                "int": "number",
                "float": "number",
                "str": "string",
                "bool": "boolean"
            }
            for param in sig.parameters.values():
                py_type = param.annotation.__name__ if param.annotation != param.empty else "string"
                openai_type = type_map.get(py_type, "string")
                prop = {"type": openai_type, "description": f"{param.name}"}
                if param.default != param.empty:
                    prop["default"] = param.default
                props[param.name] = prop
                if param.default == param.empty:
                    required.append(param.name)
            param_schema = {"type": "object", "properties": props}
            if required:
                param_schema["required"] = required
        else:
            param_schema = parameters
        _TOOL_REGISTRY.append({
            "name": tool_name,
            "description": tool_description,
            "parameters": param_schema,
            "function": f
        })
        return f
    if func:
        return decorator(func)
    return decorator

def get_registered_tools() -> List[Dict[str, Any]]:
    """
    Returns a list of registered tools with their OpenAI function schema and function reference.
    """
    return _TOOL_REGISTRY

# @function_tool
# def add_numbers(a: int, b: int) -> int:
#     """
#     Add two numbers and return the result.
#     Args:
#         a (int): First number
#         b (int): Second number
#     Returns:
#         int: The sum of a and b
#     """
#     print("[Tool] Running add number tool")
#     return a + b