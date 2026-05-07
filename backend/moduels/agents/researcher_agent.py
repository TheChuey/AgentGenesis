from moduels.manager import app_registry
import model as ollama_model
from pathlib import Path
from moduels.tools.search_tool import search_internet
from moduels.tools.scrape_tool import scrape_url

from moduels.prompt_manager import get_core_knowledge
from moduels.tools.time_tool import get_current_datetime

def get_researcher_prompt():
    """Loads the specific instructions for the researcher agent."""
    file_path = Path(__file__).parent.parent / "instructions" / "researcher_agent.md"
    base_prompt = "You are an AI Research Agent."
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        # Extract the text after # RESEARCHER_AGENT
        if "# RESEARCHER_AGENT" in content:
            base_prompt = content.split("# RESEARCHER_AGENT")[1].strip()
        else:
            base_prompt = content.strip()
            
    knowledge = get_core_knowledge()
    if knowledge:
        base_prompt += f"\n\n[SYSTEM CORE KNOWLEDGE]\n{knowledge}"
        
    current_time = get_current_datetime()
    base_prompt += f"\n\n[CURRENT SYSTEM TIME]\nThe current local date and time is: {current_time}"
        
    return base_prompt

def researcher_agent_handler(message, model_name, history=None):
    """
    Researcher Agent that uses DuckDuckGo and Web Scraping.
    """
    print(f"\n[TEST POINT] --- RESEARCHER AGENT INITIATED ---")
    if history is None:
        history = []
        
    system_prompt = get_researcher_prompt()
    
    # 1. Ask Ollama to formulate a search query based on the user's message
    print(f"[TEST POINT] Asking {model_name} to generate a search query...")
    query_prompt = f"User asked: '{message}'. Extract just the core search phrase to look up on the internet. Return ONLY the search string, no quotes or extra text."
    query_result = ollama_model.generate_response(query_prompt, model_name)
    search_query = query_result.get("response", "").strip().strip('\"\'')
    print(f"[TEST POINT] Generated Search Query: {search_query}")
    
    # 2. Execute the Search Tool
    print(f"[TEST POINT] Executing search...")
    search_results = search_internet(search_query, max_results=3)
    
    # 3. Format the tools output
    tools_context = "### INTERNET SEARCH RESULTS ###\n\n"
    if not search_results:
        tools_context += "No search results found.\n"
    else:
        for i, res in enumerate(search_results):
            tools_context += f"Result {i+1}:\nTitle: {res.get('title')}\nURL: {res.get('href')}\nSummary: {res.get('body')}\n\n"
            
            # Optional: Scrape the first result for deeper context
            if i == 0:
                print(f"[TEST POINT] Scraping top result: {res.get('href')}")
                scraped_text = scrape_url(res.get('href'), max_chars=1500)
                tools_context += f"--- Deep Scrape of Top Result ---\n{scraped_text}\n-------------------------------\n\n"

    # 4. Construct Final Prompt with History, System Prompt, and Tool Context
    history_text = ""
    for entry in history[-3:]: 
        role = "User" if entry['role'] == 'user' else "Agent"
        history_text += f"{role}: {entry['content']}\n"

    full_prompt = f"{system_prompt}\n\n{tools_context}\n[RECENT HISTORY]:\n{history_text}\nUser: {message}\nAgent:"
    
    print(f"[TEST POINT] Sending final prompt to model (Context Size: {len(tools_context)} chars)...")
    final_result = ollama_model.generate_response(full_prompt, model_name)
    
    # Prepend a small visual indicator
    original_response = final_result.get("response", "")
    final_result["response"] = f"*(🌐 Researcher Agent Web Search)*\n\n{original_response}"
    
    final_result["model"] = "RESEARCHER"
    print(f"[TEST POINT] --- RESEARCHER AGENT COMPLETE ---\n")
    return final_result

# Register this agent with the system
app_registry.register("researcher", researcher_agent_handler)
