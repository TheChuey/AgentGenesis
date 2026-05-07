from moduels.manager import app_registry
import model as ollama_model
from moduels.prompt_manager import get_core_knowledge
import chromadb
import os

RAG_CONTEXT = {
    "current_document": ""
}

def rag_agent_handler(message, model_name, history=None):
    """
    RAG Agent that uses the uploaded document context.
    Now upgraded to perform true Vector Semantic Search via ChromaDB!
    """
    if history is None:
        history = []
        
    system_prompt = "You are an expert Retrieval-Augmented Generation agent. Use the document context provided below to answer the user's question accurately. If the document does not contain the answer, explicitly state that you cannot find it in the provided documents."
    
    knowledge = get_core_knowledge()
    if knowledge:
        system_prompt += f"\n\n[SYSTEM CORE KNOWLEDGE]\n{knowledge}"
        
    # Attempt to use true Vector Search RAG
    context = ""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources", "chroma_db")
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name="rag_documents")
        
        results = collection.query(query_texts=[message], n_results=3)
        if results and results['documents'] and results['documents'][0]:
            context = "\n\n".join(results['documents'][0])
            print(f"[TEST POINT] RAG pulled {len(context)} chars from ChromaDB.")
    except Exception as e:
        print(f"[TEST POINT] RAG vector search failed or no docs: {e}")
    
    # Fallback to Volatile Memory
    if not context:
        context = RAG_CONTEXT.get("current_document", "")
        print(f"[TEST POINT] RAG pulled {len(context)} chars from volatile memory.")
        
    if not context:
        context = "No document found in memory or database."
    
    # Format chat history
    history_text = ""
    for entry in history[-3:]: 
        role = "User" if entry['role'] == 'user' else "Agent"
        history_text += f"{role}: {entry['content']}\n"
    
    # Construct prompt with system instructions and document context
    full_prompt = f"{system_prompt}\n\n[DOCUMENT CONTEXT]:\n{context}\n\n[RECENT HISTORY]:\n{history_text}\nUser: {message}\nAgent:"
    
    print(f"[RAG AGENT] Processing message using {model_name} with context size {len(context)}...")
    
    result = ollama_model.generate_response(full_prompt, model_name)
    
    # Prepend a small visual indicator so the user knows context was used
    original_response = result.get("response", "")
    result["response"] = f"*(📚 RAG Agent Vector Reference)*\n\n{original_response}"
    
    # Tag the source so UI knows it's the RAG agent
    result["model"] = "RAG"
    return result

# Register this agent with the system
app_registry.register("rag", rag_agent_handler)
