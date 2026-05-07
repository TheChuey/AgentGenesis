import inspect

TOOL_REGISTRY = {}

def tool(name=None, description=None):
    """
    A decorator to register a function as an AI tool.
    Extracts name, docstring, and arguments automatically.
    """
    def decorator(func):
        tool_name = name or func.__name__
        tool_desc = description or inspect.getdoc(func) or "No description provided."
        
        # Get function signature for future autonomous tool calling
        sig = inspect.signature(func)
        params = []
        for param_name, param in sig.parameters.items():
            params.append(param_name)
            
        TOOL_REGISTRY[tool_name] = {
            "name": tool_name,
            "description": tool_desc,
            "parameters": params,
            "func": func
        }
        
        return func
        
    return decorator
