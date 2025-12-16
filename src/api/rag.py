from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
# from langchain_mongodb import MongoDBAtlasVectorSearch # Removed for local compatibility
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from src.agent_core.config import Config
from src.api.database import get_collection

# Optional import for Gemini
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False

def get_embeddings():
    config = Config.from_env()
    if config.model_provider == "gemini" and config.gemini_api_key and HAS_GOOGLE_GENAI:
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=config.gemini_api_key)
    else:
        if config.gemini_api_key and not HAS_GOOGLE_GENAI:
            print("Warning: Google GenAI not available, falling back to Ollama")
        return OllamaEmbeddings(base_url=config.ollama_base_url, model=config.ollama_embedding_model)

def get_llm():
    config = Config.from_env()
    if config.model_provider == "gemini" and config.gemini_api_key and HAS_GOOGLE_GENAI:
        return ChatGoogleGenerativeAI(model=config.gemini_model, google_api_key=config.gemini_api_key)
    else:
        if config.gemini_api_key and not HAS_GOOGLE_GENAI:
            print("Warning: Google GenAI not available, falling back to Ollama")
        return ChatOllama(base_url=config.ollama_base_url, model=config.ollama_model)

from langchain_chroma import Chroma
import os

def get_vector_store():
    # collection = get_collection() # Not needed for Chroma
    embeddings = get_embeddings()
    config = Config.from_env()
    
    # Persist Chroma in the workspace .nova directory
    persist_directory = str(config.workspace_dir / ".nova" / "chroma_db")
    
    vector_store = Chroma(
        collection_name="nova_knowledge",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    return vector_store

def ingest_text(text: str, source: str = "user_input"):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.create_documents([text], metadatas=[{"source": source}])
    vector_store = get_vector_store()
    vector_store.add_documents(docs)
    # Chroma 0.4+ persists automatically or via specific calls depending on version, 
    # but usually safe to let it handle it.

def get_qa_chain():
    llm = get_llm()
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    prompt_template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    return chain
