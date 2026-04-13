import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    rate_limit_per_minute: int = 60
    rapidapi_proxy_secret: str = ""
    geoip_db_path: str = "data/GeoLite2-City.mmdb"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
