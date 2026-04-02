export type UploadResponse = {
  dataset_id: string;
  file_name: string;
  rows: number;
  columns: string[];
  preview: Record<string, string | number | null>[];
};

export type AnalyzeResponse = {
  profile: {
    file_name: string;
    row_count: number;
    column_count: number;
    numeric_columns: string[];
    categorical_columns: string[];
    datetime_columns: string[];
    missing_values: { column: string; missing: number }[];
    correlations: { x: string; y: string; correlation: number }[];
  };
  charts: {
    chart_type: "bar" | "line" | "pie" | "histogram";
    title: string;
    x_key: string;
    y_key?: string | null;
    description: string;
    data: Record<string, string | number | null>[];
  }[];
  quick_insights: {
    anomalies: string[];
    high_correlation_pairs: { x: string; y: string; correlation: number }[];
    top_missing_columns: { column: string; missing: number }[];
  };
  ai_insights: {
    summary: string;
    patterns: string[];
    anomalies: string[];
    business_suggestions: string[];
    recommended_questions: string[];
  };
};

export type ChatResponse = {
  answer: string;
  reasoning: string;
  follow_up: string[];
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

