from fastapi import APIRouter
from app.db import check_database_connection
from app.schemas import HealthResponse
from app.agents.navigator_client import NavigatorClient

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    db_ok = check_database_connection()
    nav_client = NavigatorClient()
    nav_status = nav_client.check_health() if nav_client.is_configured() else "unconfigured"
    
    return HealthResponse(
        status="ok",
        database="ok" if db_ok else "offline",
        fdot="ok",
        gainesville="ok",
        navigator=nav_status
    )
