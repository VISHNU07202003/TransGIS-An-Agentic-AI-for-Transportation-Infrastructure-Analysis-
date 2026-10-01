from fastapi import APIRouter
from app.db import check_database_connection
from app.schemas import HealthResponse
from app.agents.navigator_client import NavigatorClient

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        database="unprobed",
        fdot="unprobed",
        gainesville="unprobed",
        navigator="unprobed"
    )
