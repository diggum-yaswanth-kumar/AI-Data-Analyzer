"use client";

import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

type UploadZoneProps = {
  onFileSelect: (file: File) => void;
  loading: boolean;
};

export function UploadZone({ onFileSelect, loading }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  return (
    <button
      type="button"
      className={`upload-zone ${isDragging ? "dragging" : ""}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        const file = event.dataTransfer.files?.[0];
        if (file) onFileSelect(file);
      }}
      disabled={loading}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        hidden
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onFileSelect(file);
        }}
      />
      <UploadCloud size={34} />
      <div>
        <h3>Drop CSV or Excel here</h3>
        <p>Upload a dataset to generate charts, AI insights, and a PDF report.</p>
      </div>
      <span>{loading ? "Uploading..." : "Choose File"}</span>
    </button>
  );
}

