from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict
import logging

# Import all necessary functions and classes from your model file
from model import (
    graph_base_chat, 
    MessageState,
    process_pdf_and_upsert_to_qdrant,
    get_rag_chain
)
from langchain_core.messages import HumanMessage, AIMessage

# --- FastAPI App Initialization ---
app = FastAPI(
    title="REVLINE Fitness Chatbot Server",
    description="An API server for the REVLINE fitness chatbot.",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Pydantic Models for API ---
class ChatRequest(BaseModel):
    messages: List[Dict]

class RAGRequest(BaseModel):
    question: str

# --- API Endpoints ---

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Receives a PDF, processes it, and upserts it to Qdrant.
    """
    logger.info(f"Received PDF upload: {file.filename}")
    try:
        pdf_bytes = await file.read()
        process_pdf_and_upsert_to_qdrant(
            pdf_bytes=pdf_bytes, 
            collection_name="revline_fitness_docs" # Use fitness collection
        )
        return {"message": "PDF processed successfully and is ready for Q&A."}
    except Exception as e:
        logger.error(f"Error during PDF processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Handles general conversational chat.
    """
    logger.info("Received general chat request.")
    try:
        reconstructed_messages = [
            HumanMessage(content=msg["content"]) if msg["role"] == "user" 
            else AIMessage(content=msg["content"])
            for msg in request.messages
        ]
        
        input_state = MessageState(messages=reconstructed_messages)
        response_state = graph_base_chat.invoke(input_state)
        last_message = response_state['messages'][-1]
        
        return {"response": {"role": "assistant", "content": last_message.content}}

    except Exception as e:
        logger.error(f"Error in general chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat-rag")
async def rag_chat_endpoint(request: RAGRequest):
    """
    Handles RAG-based chat using the processed PDF.
    """
    logger.info(f"Received RAG chat request for question: '{request.question}'")
    try:
        rag_chain = get_rag_chain(collection_name="revline_fitness_docs") # Use fitness collection
        response_content = rag_chain.invoke(request.question)
        
        return {"response": {"role": "assistant", "content": response_content}}
    except Exception as e:
        logger.error(f"Error in RAG chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))