import json
from pathlib import Path
from uuid import uuid4

import pandas as pd

from app.config import get_settings


def load_dataframe(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(file_path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)
    raise ValueError("Unsupported file format. Please upload CSV or Excel.")


def persist_upload(file_name: str, file_bytes: bytes) -> tuple[str, pd.DataFrame]:
    settings = get_settings()
    dataset_id = str(uuid4())
    suffix = Path(file_name).suffix.lower()
    upload_dir = settings.upload_dir / dataset_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"source{suffix}"
    file_path.write_bytes(file_bytes)

    dataframe = load_dataframe(file_path)
    metadata = {
        "dataset_id": dataset_id,
        "file_name": file_name,
        "stored_file_name": file_path.name,
        "columns": dataframe.columns.tolist(),
        "rows": int(len(dataframe)),
    }
    (upload_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return dataset_id, dataframe


def get_dataset_path(dataset_id: str) -> Path:
    settings = get_settings()
    dataset_dir = settings.upload_dir / dataset_id
    if not dataset_dir.exists():
        raise FileNotFoundError("Dataset not found.")
    metadata_path = dataset_dir / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError("Dataset metadata missing.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return dataset_dir / metadata["stored_file_name"]


def get_metadata(dataset_id: str) -> dict:
    settings = get_settings()
    metadata_path = settings.upload_dir / dataset_id / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError("Dataset metadata missing.")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def read_dataset(dataset_id: str) -> tuple[pd.DataFrame, dict]:
    file_path = get_dataset_path(dataset_id)
    dataframe = load_dataframe(file_path)
    metadata = get_metadata(dataset_id)
    return dataframe, metadata
