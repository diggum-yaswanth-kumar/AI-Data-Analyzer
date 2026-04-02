from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    frontend_origin: str = "http://localhost:3000"
    max_sample_rows: int = 20
    storage_dir: Path = BASE_DIR / "storage"

    @property
    def upload_dir(self) -> Path:
        return self.storage_dir / "uploads"

    @property
    def report_dir(self) -> Path:
        return self.storage_dir / "reports"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    import os

    settings = Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
        max_sample_rows=int(os.getenv("MAX_SAMPLE_ROWS", "20")),
    )
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    return settings

