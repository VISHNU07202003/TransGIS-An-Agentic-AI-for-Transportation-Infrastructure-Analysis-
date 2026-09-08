from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

_parent_env = Path(__file__).resolve().parent.parent.parent / ".env"
_local_env = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

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
