import type { AnalyzeResponse } from "@/lib/types";

type InsightCardsProps = {
  analysis: AnalyzeResponse;
};

export function InsightCards({ analysis }: InsightCardsProps) {
  const stats = analysis.profile;

  return (
    <section className="insight-layout">
      <div className="metric-grid">
        <article className="metric-card">
          <span>Rows</span>
          <strong>{stats.row_count.toLocaleString()}</strong>
        </article>
        <article className="metric-card">
          <span>Columns</span>
          <strong>{stats.column_count}</strong>
        </article>
        <article className="metric-card">
          <span>Numeric Fields</span>
          <strong>{stats.numeric_columns.length}</strong>
        </article>
        <article className="metric-card">
          <span>AI Suggestions</span>
          <strong>{analysis.ai_insights.business_suggestions.length}</strong>
        </article>
      </div>

      <div className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">AI Summary</p>
            <h2>Executive snapshot</h2>
          </div>
        </div>
        <p className="lead-text">{analysis.ai_insights.summary}</p>
      </div>

      <div className="three-col-grid">
        <article className="panel compact insight-scroll-card">
          <h3>Patterns</h3>
          <ul className="styled-list insight-scroll-body">
            {analysis.ai_insights.patterns.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel compact insight-scroll-card">
          <h3>Anomalies</h3>
          <ul className="styled-list insight-scroll-body">
            {analysis.ai_insights.anomalies.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel compact insight-scroll-card">
          <h3>Business Suggestions</h3>
          <ul className="styled-list insight-scroll-body">
            {analysis.ai_insights.business_suggestions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  );
}
