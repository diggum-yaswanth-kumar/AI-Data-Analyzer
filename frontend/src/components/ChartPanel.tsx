"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { AnalyzeResponse } from "@/lib/types";

const palette = ["#4f46e5", "#0ea5e9", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6"];

type ChartPanelProps = {
  charts: AnalyzeResponse["charts"];
  columns: string[];
  datasetId: string;
  fileName: string;
  apiBaseUrl: string;
};

export function ChartPanel({
  charts,
  columns,
  datasetId,
  fileName,
  apiBaseUrl,
}: ChartPanelProps) {
  return (
    <section className="panel chart-grid">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Visual Analytics</p>
          <h2>Auto-generated charts</h2>
        </div>
      </div>
      <div className="chart-list">
        {charts.map((chart) => (
          <article key={chart.title} className="chart-card">
            <div className="chart-header">
              <div>
                <h3>{chart.title}</h3>
                <p>{chart.description}</p>
              </div>
            </div>
            <div className="chart-shell">
              <ResponsiveContainer width="100%" height={300}>
                {chart.chart_type === "bar" || chart.chart_type === "histogram" ? (
                  <BarChart data={chart.data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#23304a" />
                    <XAxis dataKey={chart.x_key} stroke="#94a3b8" tickLine={false} />
                    <YAxis stroke="#94a3b8" tickLine={false} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey={chart.y_key || "count"} fill="#4f46e5" radius={[10, 10, 0, 0]} />
                  </BarChart>
                ) : chart.chart_type === "line" ? (
                  <LineChart data={chart.data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#23304a" />
                    <XAxis dataKey={chart.x_key} stroke="#94a3b8" tickLine={false} />
                    <YAxis stroke="#94a3b8" tickLine={false} />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey={chart.y_key || "count"}
                      stroke="#22c55e"
                      strokeWidth={3}
                      dot={{ fill: "#86efac", r: 4 }}
                    />
                  </LineChart>
                ) : (
                  <PieChart>
                    <Pie
                      data={chart.data}
                      dataKey={chart.y_key || "count"}
                      nameKey={chart.x_key}
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      label
                    >
                      {chart.data.map((entry, index) => (
                        <Cell
                          key={`${String(entry[chart.x_key])}-${index}`}
                          fill={palette[index % palette.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                )}
              </ResponsiveContainer>
            </div>
          </article>
        ))}
      </div>
      <div className="schema-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Dataset Schema</p>
            <h2>Columns and fields</h2>
          </div>
        </div>
        <div className="schema-chip-grid">
          {columns.map((column) => (
            <span key={column} className="schema-chip">
              {column}
            </span>
          ))}
        </div>
      </div>
      <div className="report-panel">
        <div>
          <p className="eyebrow">Shareable Output</p>
          <h2>Export executive PDF report</h2>
          <p className="subtle">
            Download a polished report for {fileName} including AI insights,
            chart context, and dataset structure.
          </p>
        </div>
        <form action={`${apiBaseUrl}/report`} method="post" target="_blank">
          <input type="hidden" name="dataset_id" value={datasetId} readOnly />
          <button className="primary-button report-button" type="submit">
            Download Report PDF
          </button>
        </form>
      </div>
    </section>
  );
}
