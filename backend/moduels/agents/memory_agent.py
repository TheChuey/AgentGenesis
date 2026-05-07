import os
import chromadb
import model as ollama_model
from datetime import datetime

def commit_chat_to_memory(history, model_name):
    """
    Summarizes the chat history focusing on long term memory,
    and saves the summary to ChromaDB.
    """
    # 1. Format the conversation
    full_text = ""
    for msg in history:
        role = msg.get("role", "User").upper()
        content = msg.get("content", "")
        full_text += f"{role}: {content}\n"
        
    # 2. Instruct the LLM to summarize
    prompt = (
        "You are an expert Memory Extraction Agent. "
        "Review the following conversation and extract a concise, highly factual summary. "
        "Focus EXCLUSIVELY on capturing important facts, user preferences, conclusions, and core data points that would be valuable for long-term memory retrieval later. "
        "Ignore pleasantries, small talk, and redundant information.\n\n"
        f"[CONVERSATION START]\n{full_text}\n[CONVERSATION END]\n\n"
        "MEMORY SUMMARY:"
    )
    
    print("\n[TEST POINT] --- MEMORY AGENT INITIATED ---")
    print(f"[TEST POINT] Asking {model_name} to summarize chat for long-term memory...")
    response_data = ollama_model.generate_response(prompt, model_name)
    summary = response_data.get("response", "").strip()
    
    if not summary:
        raise ValueError("The model failed to generate a summary.")
        
    print(f"[TEST POINT] Generated Summary:\n{summary}")
    
    # 3. Save to ChromaDB
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources", "chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="long_term_memory")
    
    memory_id = f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    collection.add(
        documents=[summary],
        metadatas=[{"source": "chat_summary", "date": datetime.now().strftime("%Y-%m-%d")}],
        ids=[memory_id]
    )
    
    print(f"[TEST POINT] Summary saved to ChromaDB collection 'long_term_memory' with ID {memory_id}.")
    print("[TEST POINT] --- MEMORY AGENT COMPLETE ---\n")
    
    return f"Successfully extracted {len(summary)} characters of core facts and saved to long-term memory database (ID: {memory_id})."
