"use client";

import {
  Database,
  FileSpreadsheet,
  LoaderCircle,
  ScanSearch,
  Sparkles,
} from "lucide-react";
import { useState, useTransition } from "react";

import { ChartPanel } from "@/components/ChartPanel";
import { ChatPanel } from "@/components/ChatPanel";
import { InsightCards } from "@/components/InsightCards";
import { UploadZone } from "@/components/UploadZone";
import { analyzeDataset, uploadDataset } from "@/lib/api";
import type { AnalyzeResponse, UploadResponse } from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function Home() {
  const [upload, setUpload] = useState<UploadResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isUploading, startUploadTransition] = useTransition();
  const [isAnalyzing, startAnalyzeTransition] = useTransition();

  const handleFileSelect = (file: File) => {
    setError(null);
    setAnalysis(null);

    startUploadTransition(async () => {
      try {
        const nextUpload = await uploadDataset(file);
        setUpload(nextUpload);
        setIsChatOpen(false);
        startAnalyzeTransition(async () => {
          try {
            const nextAnalysis = await analyzeDataset(nextUpload.dataset_id);
            setAnalysis(nextAnalysis);
          } catch (analysisError) {
            setError(
              analysisError instanceof Error
                ? analysisError.message
                : "Analysis failed.",
            );
          }
        });
      } catch (uploadError) {
        setError(
          uploadError instanceof Error ? uploadError.message : "Upload failed.",
        );
      }
    });
  };

  return (
    <main className="app-shell">
      <section className="hero-shell">
        <div className="hero-card">
          <div className="hero-copy">
            <div className="badge">
              <Sparkles size={14} />
              AI-Powered Analytics Workspace
            </div>
            <h1>Data Insight AI</h1>
            <p>
              Turn raw CSV and Excel files into polished charts, executive
              summaries, anomaly detection, and natural-language answers in one
              professional workspace.
            </p>
          </div>
          <div className="hero-feature-grid">
            <article className="hero-feature">
              <FileSpreadsheet size={20} />
              <div>
                <h3>Upload and preview</h3>
                <p>Inspect tabular data before analysis starts.</p>
              </div>
            </article>
            <article className="hero-feature">
              <ScanSearch size={20} />
              <div>
                <h3>AI insights</h3>
                <p>Generate summaries, patterns, and business suggestions.</p>
              </div>
            </article>
            <article className="hero-feature">
              <Database size={20} />
              <div>
                <h3>Chart-backed analysis</h3>
                <p>Visualize grouped values, shares, and distributions.</p>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section className="upload-board panel">
        <div className="panel-heading upload-heading">
          <div>
            <p className="eyebrow">Data Intake</p>
            <h2>Upload and preview your dataset</h2>
          </div>
          <div className="mini-stats">
            <span>CSV / XLSX</span>
            <span>Gemini + Pandas</span>
          </div>
        </div>
        <UploadZone onFileSelect={handleFileSelect} loading={isUploading} />
        {error && <p className="error-banner">{error}</p>}

        {(isUploading || isAnalyzing) && (
          <div className="loading-row">
            <LoaderCircle className="spin" size={20} />
            <span>
              {isUploading ? "Uploading dataset..." : "Generating AI insights..."}
            </span>
          </div>
        )}

        {upload && (
          <div className="preview-wrap">
            <div className="preview-meta">
              <div>
                <p className="eyebrow">Current dataset</p>
                <h3>{upload.file_name}</h3>
              </div>
              <div className="meta-pills">
                <span>{upload.rows.toLocaleString()} rows</span>
                <span>{upload.columns.length} fields</span>
              </div>
            </div>

            <div className="table-shell">
              <table>
                <thead>
                  <tr>
                    {upload.columns.map((column) => (
                      <th key={column}>{column}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {upload.preview.map((row, index) => (
                    <tr key={index}>
                      {upload.columns.map((column) => (
                        <td key={column}>{String(row[column] ?? "-")}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      {analysis && (
        <>
          <InsightCards analysis={analysis} />
          <ChartPanel
            charts={analysis.charts}
            columns={upload?.columns || []}
            datasetId={upload?.dataset_id || ""}
            fileName={upload?.file_name || "dataset"}
            apiBaseUrl={API_BASE_URL}
          />
        </>
      )}

      {analysis && upload && (
        <ChatPanel
          datasetId={upload.dataset_id}
          suggestions={analysis.ai_insights.recommended_questions}
          isOpen={isChatOpen}
          onToggle={() => setIsChatOpen((current) => !current)}
        />
      )}
    </main>
  );
}
