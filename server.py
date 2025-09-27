from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fitness-related keywords for basic validation
FITNESS_KEYWORDS = {
    'fitness', 'exercise', 'workout', 'nutrition', 'diet', 'health', 'wellness', 'training', 
    'muscle', 'strength', 'cardio', 'yoga', 'pilates', 'running', 'walking', 'swimming',
    'weight', 'calories', 'protein', 'carbs', 'vitamins', 'supplements', 'gym', 'sports',
    'athletic', 'performance', 'recovery', 'injury', 'rehabilitation', 'physical', 'body',
    'metabolism', 'endurance', 'flexibility', 'balance', 'coordination', 'posture', 'core',
    'abs', 'legs', 'arms', 'chest', 'back', 'shoulders', 'biceps', 'triceps', 'quadriceps',
    'hamstrings', 'glutes', 'pushups', 'squats', 'deadlifts', 'bench', 'press', 'curl',
    'stretch', 'warm', 'cool', 'rest', 'sleep', 'hydration', 'meal', 'eating', 'food',
    'healthy', 'fit', 'strong', 'lean', 'bulk', 'cut', 'fat', 'loss', 'gain', 'mass'
}

def is_fitness_related(text: str) -> bool:
    """Check if the text contains fitness-related keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in FITNESS_KEYWORDS)

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
    Handles general conversational chat with fitness topic validation.
    """
    logger.info("Received general chat request.")
    try:
        # Get the last user message to check if it's fitness-related
        user_messages = [msg for msg in request.messages if msg["role"] == "user"]
        if user_messages:
            last_user_message = user_messages[-1]["content"]
            
            # If the question is not fitness-related, return a polite redirect
            if not is_fitness_related(last_user_message):
                return {
                    "response": {
                        "role": "assistant", 
                        "content": "I'm REVLINE, a specialized fitness assistant. I can only help with fitness, exercise, nutrition, and wellness topics. Please ask me something related to your health and fitness journey!"
                    }
                }
        
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
    Handles RAG-based chat using the processed PDF with fitness topic validation.
    """
    logger.info(f"Received RAG chat request for question: '{request.question}'")
    try:
        # Validate if the question is fitness-related
        if not is_fitness_related(request.question):
            return {
                "response": {
                    "role": "assistant", 
                    "content": "I'm REVLINE, a specialized fitness assistant. I can only help analyze fitness, exercise, nutrition, and wellness content. Please ask questions related to fitness topics about your uploaded document."
                }
            }
        
        rag_chain = get_rag_chain(collection_name="revline_fitness_docs") # Use fitness collection
        response_content = rag_chain.invoke(request.question)
        
        return {"response": {"role": "assistant", "content": response_content}}
    except Exception as e:
        logger.error(f"Error in RAG chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)