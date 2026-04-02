from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import get_settings
from app.models import AnalyzeRequest, ChatRequest
from app.services.analyzer import analyze_dataset, build_preview, chat_with_dataset
from app.services.reporting import generate_report
from app.utils.data_store import persist_upload, read_dataset


settings = get_settings()
app = FastAPI(title="Data Insight AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required.")
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported.")

    try:
        file_bytes = await file.read()
        dataset_id, dataframe = persist_upload(file.filename, file_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "dataset_id": dataset_id,
        "file_name": file.filename,
        "rows": int(len(dataframe)),
        "columns": dataframe.columns.tolist(),
        "preview": build_preview(dataframe, limit=8),
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        dataframe, metadata = read_dataset(request.dataset_id)
        return analyze_dataset(dataframe, metadata["file_name"])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        dataframe, _ = read_dataset(request.dataset_id)
        return chat_with_dataset(dataframe, request.question)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/report")
def report(dataset_id: str = Form(...)):
    try:
        dataframe, metadata = read_dataset(dataset_id)
        analysis = analyze_dataset(dataframe, metadata["file_name"])
        report_path = generate_report(dataset_id, metadata["file_name"], analysis)
        return FileResponse(report_path, media_type="application/pdf", filename=f"{metadata['file_name']}-report.pdf")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
