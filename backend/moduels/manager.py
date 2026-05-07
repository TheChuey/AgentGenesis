class SystemRegistry:
    def __init__(self):
        self.handlers = {} # Map: { "mode_id": python_function }

    def register(self, mode_id, handler_func):
        """Registers a logic module."""
        self.handlers[mode_id] = handler_func
        print(f"[TEST POINT] Module Registered: {mode_id}") # Debugging point

    def run(self, mode_id, message, model_name, history=None):
        """Routes traffic to the correct module."""
        if history is None:
            history = []
            
        if mode_id not in self.handlers:
            print(f"[ERROR] Mode '{mode_id}' not found. Defaulting to 'chat'.")
            mode_id = "chat"
        
        # Executes the specific agent function
        return self.handlers[mode_id](message, model_name, history)

# Create a shared instance
app_registry = SystemRegistry()