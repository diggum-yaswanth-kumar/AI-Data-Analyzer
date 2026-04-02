import type { AnalyzeResponse, ChatResponse, UploadResponse } from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Something went wrong.");
  }
  return response.json() as Promise<T>;
}

export async function uploadDataset(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<UploadResponse>(response);
}

export async function analyzeDataset(datasetId: string): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId }),
  });

  return parseResponse<AnalyzeResponse>(response);
}

export async function chatWithDataset(
  datasetId: string,
  question: string,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, question }),
  });

  return parseResponse<ChatResponse>(response);
}
