from moduels.manager import app_registry
import model as ollama_model
from moduels.prompt_manager import get_system_prompt

def basic_agent_handler(message, model_name, history=None):
    """
    A foundational agent you can customize.
    This demonstrates how to build a basic agent.
    """
    if history is None:
        history = []
        
    system_prompt = get_system_prompt("BASIC_AGENT")
    
    # Format chat history
    history_text = ""
    for entry in history[-5:]: # Keep last 5 messages for context
        role = "User" if entry['role'] == 'user' else "Agent"
        history_text += f"{role}: {entry['content']}\n"
    
    # Construct prompt with system instructions
    full_prompt = f"{system_prompt}\n\nRecent History:\n{history_text}\nUser: {message}\nAgent:"
    
    print(f"[BASIC AGENT] Processing message using {model_name}...")
    
    result = ollama_model.generate_response(full_prompt, model_name)
    
    # You can add custom parsing or actions here
    
    # Tag the source so UI knows it's the basic agent
    result["model"] = "BASIC_AGENT"
    return result

# Register this agent with the system
app_registry.register("basic_agent", basic_agent_handler)
