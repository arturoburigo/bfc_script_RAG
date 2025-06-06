from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.core.integrated_rag_system import OptimizedSearchSystem
from app.core.initialize_chroma_db import initialize_chroma_db
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG System API",
    description="API para o Sistema RAG Otimizado",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class GenerateRequest(BaseModel):
    query: str
    top_k: int = 5

class GenerateResponse(BaseModel):
    llm_response: str

def get_search_system() -> OptimizedSearchSystem:
    """Dependency to get or initialize the search system"""
    try:
        system = OptimizedSearchSystem()
        if not system.is_initialized:
            system.initialize_database(reset_collections=False)
        return system
    except Exception as e:
        logger.error(f"Error initializing search system: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize search system")

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde da API"""
    return {"status": "healthy"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest, system: OptimizedSearchSystem = Depends(get_search_system)):
    """Endpoint para gerar respostas usando o LLM"""
    try:
        response = system.generate_llm_response(
            query_text=request.query,
            top_k=request.top_k
        )
        return GenerateResponse(llm_response=response["llm_response"])
    except Exception as e:
        logger.error(f"Error in generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/initialize")
async def initialize_database(system: OptimizedSearchSystem = Depends(get_search_system)):
    """Endpoint para inicializar o banco de dados"""
    try:
        stats = initialize_chroma_db(reset_collections=True)
        return {
            "status": "success",
            "message": "Database initialized successfully",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 