from flask import Flask
import os
from moduels.manager import app_registry
from routes.chat_api import chat_bp # Import our separated API logic[cite: 8]
import model # Your Ollama logic helper
# Import agents to register them
import moduels.agents.basic_agent
import moduels.agents.rag_agent
import moduels.agents.researcher_agent
import moduels.agents.recall_agent

app = Flask(__name__)

# 1. REGISTER THE BLUEPRINT (Logic Wing)[cite: 8]
# All routes in chat_api.py will now start with /api (e.g., /api/chat)
app.register_blueprint(chat_bp, url_prefix='/api')

# 2. PLUG IN THE MODES (The Registry)[cite: 8]
# Agents are registered within their respective module files inside moduels/agents/

# 3. STATIC FILE SERVING[cite: 8]
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

@app.route('/')
def home():
    from flask import send_from_directory
    return send_from_directory(frontend_dir, "index.html")

# CATCH-ALL for JS/CSS[cite: 8]
@app.route('/frontend/<path:path>')
def assets(path):
    from flask import send_from_directory
    return send_from_directory(frontend_dir, path)

if __name__ == "__main__":
    app.run(port=5000, debug=True)