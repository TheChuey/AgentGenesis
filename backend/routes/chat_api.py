from flask import Blueprint, request, jsonify
from moduels.manager import app_registry
import model as ollama_model
import os

chat_bp = Blueprint('chat_api', __name__)

@chat_bp.route('/chat', methods=['POST'])
def handle_chat():
    data = request.json
    mode = data.get("mode", "chat") # Identifies WHICH agent to use
    msg = data.get("message")
    model = data.get("model")
    history = data.get("history", [])

    # TEST POINT: Verify incoming payload
    print(f"[TEST POINT] Incoming API Call -> Mode: {mode}, Model: {model}")

    try:
        # Ask the registry to find and run the logic
        result = app_registry.run(mode, msg, model, history)
        return jsonify({
            "source": result.get("model", mode.upper()),
            "reply": result.get("response", "No reply")
        })
    except Exception as e:
        print(f"[ERROR] Execution failed: {str(e)}")
        return jsonify({"source": "SYSTEM", "reply": f"Error: {str(e)}"}), 500

@chat_bp.route('/models', methods=['GET'])
def get_models():
    models = ollama_model.get_running_models()
    return jsonify({"models": models})

@chat_bp.route('/modes', methods=['GET'])
def get_modes():
    # Return registered modes
    modes = [{"id": k, "name": k.replace("_", " ").upper()} for k in app_registry.handlers.keys()]
    return jsonify({"modes": modes})

@chat_bp.route('/memory/commit', methods=['POST'])
def commit_memory():
    data = request.json
    history = data.get("history", [])
    model = data.get("model", "qwen2.5-coder")
    
    if not history:
        return jsonify({"status": "error", "reply": "No conversation to memorize."})
        
    try:
        from moduels.agents.memory_agent import commit_chat_to_memory
        result_msg = commit_chat_to_memory(history, model)
        return jsonify({"status": "success", "reply": result_msg})
    except Exception as e:
        print(f"[ERROR] Memory commit failed: {str(e)}")
        return jsonify({"status": "error", "reply": f"Failed to commit memory: {str(e)}"}), 500

@chat_bp.route('/memory/wipe', methods=['DELETE'])
def wipe_memory():
    try:
        import chromadb
        import os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "chroma_db")
        client = chromadb.PersistentClient(path=db_path)
        
        # Delete collections if they exist
        try:
            client.delete_collection(name="long_term_memory")
        except Exception:
            pass
            
        try:
            client.delete_collection(name="rag_documents")
        except Exception:
            pass
            
        return jsonify({"status": "success", "reply": "All long-term memories and RAG documents have been permanently deleted from ChromaDB."})
    except Exception as e:
        print(f"[ERROR] Memory wipe failed: {str(e)}")
        return jsonify({"status": "error", "reply": f"Failed to wipe memory: {str(e)}"}), 500

@chat_bp.route('/mode', methods=['POST'])
def set_mode():
    return jsonify({"status": "success"})

@chat_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"reply": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"reply": "No selected file"}), 400
        
    text_content = ""
    try:
        if file.filename.endswith(".pdf"):
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        else:
            text_content = file.read().decode('utf-8', errors='ignore')
            
        # Store it globally for the immediate RAG agent
        from moduels.agents.rag_agent import RAG_CONTEXT
        RAG_CONTEXT["current_document"] = text_content[:15000] 
        
        # ALSO save it to the permanent ChromaDB!
        import chromadb
        import os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "chroma_db")
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(name="rag_documents")
        
        doc_id = f"doc_{file.filename.replace(' ', '_')}"
        collection.add(
            documents=[text_content[:40000]], # ChromaDB can hold much more than the context window
            metadatas=[{"filename": file.filename}],
            ids=[doc_id]
        )
        
        return jsonify({"reply": f"{file.filename} loaded to active memory AND saved to permanent ChromaDB!"})
    except Exception as e:
        return jsonify({"reply": f"Upload failed: {str(e)}"}), 500