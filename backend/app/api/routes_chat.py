from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.agents.agent import TransportationAgent
from app.db import check_database_connection

router = APIRouter(prefix="/api")

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat endpoint for asking natural language transportation questions."""
    db = None
    if check_database_connection():
        from app.db import SessionLocal
        try:
            db = SessionLocal()
        except Exception:
            db = None

    try:
        agent = TransportationAgent()
        response = agent.process_query(request, db)
        return response
    finally:
        if db:
            db.close()
