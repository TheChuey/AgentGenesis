# backend/rag_service.py

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader

vector_db = None

def process_pdf_to_memory(file_path: str):
    global vector_db

    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return "PDF loaded. RAG ready."

def query_rag(question: str):
    global vector_db

    if vector_db is None:
        return "No PDF loaded."

    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
You are an expert assistant.

Use ONLY this context:
{context}

Question:
{question}

Answer:
"""

    llm = OllamaLLM(model="qwen2.5-coder")
    return llm.invoke(prompt)