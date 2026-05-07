import os
import chromadb
from moduels.manager import app_registry
import model as ollama_model
from moduels.prompt_manager import get_core_knowledge
from moduels.tools.time_tool import get_current_datetime

def recall_agent_handler(message, model_name, history=None):
    if history is None:
        history = []
        
    print("\n[TEST POINT] --- RECALL AGENT INITIATED ---")
    
    # 1. Access ChromaDB
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources", "chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    
    memory_context = ""
    
    # Retrieve from Long Term Memory (Summarized Chats)
    try:
        mem_collection = client.get_collection(name="long_term_memory")
        mem_results = mem_collection.query(query_texts=[message], n_results=2)
        if mem_results and mem_results['documents'] and mem_results['documents'][0]:
            memory_context += "### RECOVERED PAST CONVERSATION MEMORIES ###\n"
            for doc in mem_results['documents'][0]:
                memory_context += f"- {doc}\n\n"
    except Exception as e:
        print(f"[TEST POINT] No long_term_memory collection found or error: {e}")

    # Retrieve from RAG Documents
    try:
        rag_collection = client.get_collection(name="rag_documents")
        rag_results = rag_collection.query(query_texts=[message], n_results=2)
        if rag_results and rag_results['documents'] and rag_results['documents'][0]:
            memory_context += "### RECOVERED DOCUMENT FRAGMENTS ###\n"
            for doc in rag_results['documents'][0]:
                memory_context += f"- {doc}\n\n"
    except Exception as e:
        print(f"[TEST POINT] No rag_documents collection found or error: {e}")

    if not memory_context:
        memory_context = "No relevant long-term memories or documents found in ChromaDB.\n"

    # 2. Build Prompt
    system_prompt = (
        "You are an AI Recall Agent with direct access to the user's permanent ChromaDB vector database. "
        "Use the recovered memories and document fragments provided below to answer the user's message accurately. "
        "If the memories do not contain the answer, you can rely on your general knowledge but clarify that it is not from memory."
    )
    
    knowledge = get_core_knowledge()
    if knowledge:
        system_prompt += f"\n\n[SYSTEM CORE KNOWLEDGE]\n{knowledge}"
        
    current_time = get_current_datetime()
    system_prompt += f"\n\n[CURRENT SYSTEM TIME]\nThe current local date and time is: {current_time}"
    
    history_text = ""
    for entry in history[-3:]: 
        role = "User" if entry['role'] == 'user' else "Agent"
        history_text += f"{role}: {entry['content']}\n"
        
    full_prompt = f"{system_prompt}\n\n{memory_context}\n[RECENT HISTORY]:\n{history_text}\nUser: {message}\nAgent:"
    
    print(f"[TEST POINT] Sending prompt to model (Context Size: {len(memory_context)} chars)...")
    final_result = ollama_model.generate_response(full_prompt, model_name)
    
    # Visual Indicator
    original_response = final_result.get("response", "")
    final_result["response"] = f"*(🧠 Recall Agent accessed ChromaDB)*\n\n{original_response}"
    final_result["model"] = "RECALL"
    
    print("[TEST POINT] --- RECALL AGENT COMPLETE ---\n")
    return final_result

# Register the agent
app_registry.register("recall", recall_agent_handler)
