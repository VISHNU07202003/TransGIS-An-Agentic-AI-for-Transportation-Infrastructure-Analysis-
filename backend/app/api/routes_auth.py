from fastapi import APIRouter, Request
from app.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["access"])

@router.get("/config")
def config():
    return {"required": get_settings().auth_mode == "required"}

@router.get("/me")
def me(request: Request):
    return {"subject": request.state.principal.subject, "role": request.state.principal.role}
