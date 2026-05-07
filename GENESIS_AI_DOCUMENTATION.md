# GenesisAI Framework Documentation

Welcome to the GenesisAI Framework! This document explains the exact file structure of your application, how the advanced prompt chain works behind the scenes, and how you can easily create new AI Agents in the future.

---

## 📂 File Structure

```text
GenesisAI/
│
├── requirments.txt           # Python dependencies (Flask, requests, PyPDF2, chromadb, etc.)
│
├── frontend/                 # Client-side UI
│   ├── index.html            # Main UI layout (Sidebar, Chat Window)
│   ├── style.css             # UI styling and dynamic theme colors
│   ├── script.js             # Core frontend logic (Button clicks, API fetching)
│   ├── api_helper.js         # Wrapper for sending REST requests to the backend
│   └── ui_manager.js         # Handles DOM manipulation, chat bubbles, and mode themes
│
└── backend/                  # Server-side Python Application
    ├── server.py             # Flask Entry Point. Starts the server and imports agents.
    ├── model.py              # Connects directly to your local Ollama instance
    │
    ├── routes/               
    │   └── chat_api.py       # API Endpoints (/api/chat, /api/upload, /api/memory/commit)
    │
    ├── resources/
    │   ├── system_prompts.md # Contains default base prompts for agents
    │   └── chroma_db/        # Your persistent, local vector database!
    │
    └── moduels/              # The Core Intelligence Engine
        ├── manager.py        # The Registry. Connects a UI "Mode" to a Python "Agent"
        ├── prompt_manager.py # Utility that builds background prompts and injects Core Knowledge
        │
        ├── agents/           # YOUR MODULAR AI AGENTS
        │   ├── basic_agent.py      # Standard conversational agent
        │   ├── rag_agent.py        # Queries the database for document chunks
        │   ├── researcher_agent.py # Connects to DuckDuckGo and web scrapes
        │   ├── memory_agent.py     # Special utility agent that summarizes and saves to Chroma
        │   └── recall_agent.py     # Queries Chroma for long-term memories
        │
        ├── tools/            # PYTHON TOOLS (Functions your agents can use)
        │   ├── __init__.py         # Contains the custom `@tool` decorator
        │   ├── search_tool.py      # DuckDuckGo search function
        │   ├── scrape_tool.py      # BeautifulSoup URL scraping function
        │   └── time_tool.py        # Returns the current local system time
        │
        └── instructions/     # MARKDOWN INSTRUCTIONS
            ├── core_knowledge.md   # Global facts about the user (e.g., your name, preferences)
            └── researcher_agent.md # Complex system instructions for specific agents
```

---

## 🔗 How The Prompt Chain Works

When you type a message into the frontend and hit send, here is the exact lifecycle of how the prompt is built and executed:

1. **The Request**: The frontend bundles your `message`, the active `mode` (e.g., "researcher"), your selected `model` (e.g., "qwen2.5-coder"), and your `history` array. It sends this to the `/api/chat` endpoint.
2. **The Registry**: `chat_api.py` receives the data and asks the `app_registry` to find the correct agent handler based on the mode.
3. **The Agent Chain**: The specific agent (e.g., `researcher_agent_handler`) activates and begins building the **Prompt Chain**:
    - **Base Prompt**: It grabs its fundamental personality instructions (e.g., "You are an expert Research Agent").
    - **Global Context Injection**: It calls `get_core_knowledge()` and `get_current_datetime()` to silently inject `[SYSTEM CORE KNOWLEDGE]` and `[CURRENT SYSTEM TIME]` into the background.
    - **Tool Execution (Action Phase)**: The agent runs its specific Python code. (e.g., The researcher takes your message, runs a DuckDuckGo search, scrapes a website, and formats that data into a `[CONTEXT]` string).
    - **History Injection**: It formats the last 3 messages of your `history` so it understands what you were just talking about.
    - **The Final Assembly**: It concatenates everything into one massive string:
      ```text
      {System Prompt}
      {Core Knowledge}
      {System Time}
      {Tool/Database Context}
      {Recent Chat History}
      User: {Message}
      Agent:
      ```
4. **Execution**: The agent passes this final compiled string to `model.generate_response()`, which asks Ollama to complete the text.
5. **Formatting**: Ollama returns the raw text. The Agent prepends a visual indicator (like `*(🌐 Researcher Agent Web Search)*`) and returns it to the frontend!

---

## 🛠️ How to Code a New Agent in the Future

Because of the modular framework we built, adding a completely new agent with new capabilities is incredibly easy. You don't have to touch the frontend, the API, or the Ollama connection.

If you want to build an agent that, for example, reads your local computer files:

**Step 1: Create the Agent File**
Create `backend/moduels/agents/file_reader_agent.py`.

**Step 2: Write the Handler Function**
```python
from moduels.manager import app_registry
import model as ollama_model
from moduels.prompt_manager import get_system_prompt

def file_reader_handler(message, model_name, history=None):
    if history is None: history = []
    
    # 1. Build your system prompt (you can inject Core Knowledge here too)
    system_prompt = "You are an AI that reads local computer files to answer questions."
    
    # 2. Execute any tools you want! (e.g., python code to read a file based on the message)
    file_contents = "..." # (Imagine you used python to read C:/example.txt here)
    
    # 3. Assemble the Prompt Chain
    full_prompt = f"{system_prompt}\n\n[FILE CONTENTS]:\n{file_contents}\n\nUser: {message}\nAgent:"
    
    # 4. Generate the response
    result = ollama_model.generate_response(full_prompt, model_name)
    
    # 5. Add a visual indicator
    original = result.get("response", "")
    result["response"] = f"*(📂 File Reader Agent)*\n\n{original}"
    
    return result

# 6. Register it!
app_registry.register("file_reader", file_reader_handler)
```

**Step 3: Plug it into the Server**
Open `backend/server.py` and simply import it at the top:
```python
import moduels.agents.basic_agent
import moduels.agents.rag_agent
import moduels.agents.researcher_agent
import moduels.agents.recall_agent
import moduels.agents.file_reader_agent # <--- Your new agent!
```

**That's it!** The moment you save `server.py`, the backend will restart, the frontend dropdown will automatically populate with `FILE READER`, and you can start using it immediately!
