from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
from typing import Literal

_parent_env = Path(__file__).resolve().parent.parent.parent / ".env"
_local_env = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    auth_mode: Literal["disabled", "required"] = "disabled"
    # JSON [{"subject":"alice","sha256":"...","role":"analyst"}]. Store only token hashes.
    auth_tokens_json: str = "[]"
    state_database_url: str = "sqlite:///./transgis_state.db"
    rate_limit_per_minute: int = Field(default=120, ge=1, le=10000)
    analysis_limit_per_minute: int = Field(default=10, ge=1, le=1000)
    cache_ttl_seconds: int = Field(default=3600, ge=1)
    cache_max_entries: int = Field(default=5000, ge=10)
    provider_timeout_seconds: float = Field(default=12, ge=1, le=60)
    circuit_failure_threshold: int = Field(default=3, ge=1)
    circuit_reset_seconds: int = Field(default=60, ge=1)
    job_workers: int = Field(default=1, ge=1, le=4)
    job_queue_limit: int = Field(default=100, ge=1)
    job_deadline_seconds: int = Field(default=180, ge=30, le=600)
    job_retention_seconds: int = Field(default=86400, ge=600)
    schema_check_interval_seconds: int = Field(default=86400, ge=60)
    background_workers_enabled: bool = True
    schema_monitor_enabled: bool = True
    spatial_database_enabled: bool = False
    default_intersection_radius_m: float = Field(default=250, ge=25, le=2000)
    default_traffic_site_radius_m: float = Field(default=500, ge=25, le=5000)

    @model_validator(mode="after")
    def production_requirements(self):
        if self.app_env == "production":
            if self.auth_mode != "required" or self.auth_tokens_json == "[]":
                raise ValueError("Production requires AUTH_MODE=required and individual hashed access tokens")
            if not self.state_database_url.startswith("postgresql"):
                raise ValueError("Production requires PostgreSQL STATE_DATABASE_URL for shared operational state")
            if "change_me" in self.state_database_url or "change_me" in self.database_url:
                raise ValueError("Replace default database passwords before production")
        return self

    database_url: str = "postgresql+psycopg://transportation_app:change_me@localhost:5432/transportation"
    postgres_db: str = "transportation"
    postgres_user: str = "transportation_app"
    postgres_password: str = "change_me"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    navigator_toolkit_api_key: str = ""
    navigator_base_url: str = "https://api.ai.it.ufl.edu/v1"
    navigator_model: str = ""

    geocoder_base_url: str = "https://nominatim.openstreetmap.org"
    geocoder_api_key: str = ""
    place_geocoder_base_url: str = "https://photon.komoot.io"

    fdot_rci_base_url: str = "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer"
    fdot_traffic_base_url: str = "https://www.fdot.gov/statistics/trafficinfo/default.shtm"

    gainesville_data_base_url: str = "https://data.cityofgainesville.org"
    gainesville_traffic_dataset_id: str = "pfc3-w5ih"

    model_config = SettingsConfigDict(
        env_file=(str(_parent_env), str(_local_env), ".env", "../.env"),
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
