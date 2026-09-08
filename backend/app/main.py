from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import routes_health, routes_chat, routes_locations, routes_data
from app.config import get_settings
from app.logging_config import setup_logging

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.log_level)
    logging.info("Starting up Transportation Infrastructure Analysis API")
    yield
    logging.info("Shutting down Transportation Infrastructure Analysis API")

app = FastAPI(title="Transportation Infrastructure Analysis API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_chat.router)
app.include_router(routes_locations.router)
app.include_router(routes_data.router)
