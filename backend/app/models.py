from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    dataset_id: str


class ChatRequest(BaseModel):
    dataset_id: str
    question: str = Field(min_length=2)


class ReportRequest(BaseModel):
    dataset_id: str


class ChartConfig(BaseModel):
    chart_type: str
    title: str
    x_key: str
    y_key: str | None = None
    description: str
    data: list[dict[str, Any]]
