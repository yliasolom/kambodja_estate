from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json

from services.property_parser import parse_property_from_url
from services.knowledge_base import get_relevant_knowledge
from services.openai_service import call_openai, stream_openai_response

app = FastAPI(
    title="Cambodia Property Explainer API",
    description="API for explaining property ownership to foreign buyers",
    version="2.0.0"
)

# CORS middleware to allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    """Request model for asking a question"""
    property_url: str
    question: str

class QuestionResponse(BaseModel):
    """Response model for answers"""
    answer: str
    property: dict
    
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cambodia Property Explainer API",
        "version": "2.0.0",
        "endpoints": {
            "ask": "/api/ask",
            "docs": "/docs"
        }
    }

@app.post("/api/ask/stream")
async def ask_question_stream(request: QuestionRequest):
    """
    Streaming endpoint: Answer a question with streaming response
    """
    try:
        # Parse property data
        print(f"Parsing property from: {request.property_url}")
        property_data = await parse_property_from_url(request.property_url)
        
        # Get relevant knowledge
        print(f"Loading knowledge base for {property_data.type}")
        knowledge = get_relevant_knowledge(property_data, request.question)
        
        # Stream response
        async def generate():
            # Send property data first
            yield f"data: {json.dumps({'type': 'property', 'data': property_data.dict()})}\n\n"
            
            # Stream answer
            async for chunk in stream_openai_response(property_data, knowledge, request.question):
                yield f"data: {json.dumps({'type': 'answer', 'data': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for smooth streaming
            
            # Send done signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Main endpoint: Answer a question about a specific property
    
    Steps:
    1. Parse property data from URL
    2. Load relevant knowledge base
    3. Generate answer using OpenAI
    4. Return answer + property data
    """
    try:
        # Step 1: Parse property data
        print(f"Parsing property from: {request.property_url}")
        property_data = await parse_property_from_url(request.property_url)
        
        # Step 2: Get relevant knowledge
        print(f"Loading knowledge base for {property_data.type}")
        knowledge = get_relevant_knowledge(property_data, request.question)
        
        # Step 3: Generate answer
        print(f"Generating answer for question: {request.question}")
        answer = await call_openai(property_data, knowledge, request.question)
        
        # Step 4: Return response
        return QuestionResponse(
            answer=answer,
            property=property_data.dict()
        )
        
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
