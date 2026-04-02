from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.config import get_settings
from app.models import ChartConfig
from app.services.gemini import gemini_service


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def build_preview(dataframe: pd.DataFrame, limit: int = 10) -> list[dict[str, Any]]:
    return [
        {column: _clean_value(value) for column, value in record.items()}
        for record in dataframe.head(limit).to_dict(orient="records")
    ]


def infer_datetime_columns(dataframe: pd.DataFrame) -> list[str]:
    detected: list[str] = []
    for column in dataframe.columns:
        series = dataframe[column]
        if pd.api.types.is_numeric_dtype(series):
            continue
        if pd.api.types.is_datetime64_any_dtype(series):
            detected.append(column)
            continue
        if series.dtype == "object" or pd.api.types.is_string_dtype(series):
            converted = pd.to_datetime(series, errors="coerce", format="mixed")
            if converted.notna().sum() > len(dataframe) * 0.6:
                detected.append(column)
    return detected


def build_profile(dataframe: pd.DataFrame, file_name: str) -> dict[str, Any]:
    numeric_columns = dataframe.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = dataframe.select_dtypes(exclude=["number", "datetime"]).columns.tolist()
    datetime_columns = infer_datetime_columns(dataframe)

    missing = dataframe.isna().sum().sort_values(ascending=False)
    column_stats: dict[str, Any] = {}
    for column in dataframe.columns:
        series = dataframe[column]
        stats: dict[str, Any] = {
            "dtype": str(series.dtype),
            "missing": int(series.isna().sum()),
            "unique": int(series.nunique(dropna=True)),
        }
        if column in numeric_columns:
            stats.update(
                {
                    "mean": _clean_value(series.mean()),
                    "median": _clean_value(series.median()),
                    "min": _clean_value(series.min()),
                    "max": _clean_value(series.max()),
                    "std": _clean_value(series.std()),
                }
            )
        else:
            stats["top_values"] = [
                {"label": _clean_value(index), "count": int(value)}
                for index, value in series.astype("string").value_counts(dropna=True).head(5).items()
            ]
        column_stats[column] = stats

    correlation_pairs: list[dict[str, Any]] = []
    if len(numeric_columns) >= 2:
        corr = dataframe[numeric_columns].corr(numeric_only=True)
        seen: set[tuple[str, str]] = set()
        for first in corr.columns:
            for second in corr.index:
                if first == second or (second, first) in seen:
                    continue
                value = corr.loc[second, first]
                if pd.notna(value) and abs(value) >= 0.5:
                    correlation_pairs.append(
                        {"x": first, "y": second, "correlation": round(float(value), 3)}
                    )
                    seen.add((first, second))

    return {
        "file_name": file_name,
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "datetime_columns": datetime_columns,
        "missing_values": [
            {"column": column, "missing": int(count)}
            for column, count in missing.head(8).items()
            if int(count) > 0
        ],
        "column_stats": column_stats,
        "correlations": correlation_pairs[:10],
        "sample_rows": build_preview(dataframe, get_settings().max_sample_rows),
    }


def _aggregate_for_chart(dataframe: pd.DataFrame, x_key: str, y_key: str | None = None, limit: int = 10):
    if y_key:
        grouped = dataframe.groupby(x_key, dropna=False)[y_key].sum().sort_values(ascending=False).head(limit)
        return [
            {x_key: _clean_value(index), y_key: _clean_value(value)}
            for index, value in grouped.items()
        ]
    counts = dataframe[x_key].astype("string").value_counts(dropna=False).head(limit)
    return [{x_key: _clean_value(index), "count": int(value)} for index, value in counts.items()]


def _pick_category_column(dataframe: pd.DataFrame, columns: list[str]) -> str | None:
    if not columns:
        return None
    candidate_pool: list[tuple[str, int]] = []
    for column in columns:
        unique_count = int(dataframe[column].nunique(dropna=True))
        if unique_count <= 1:
            continue
        if unique_count <= min(12, max(4, len(dataframe) // 2)):
            candidate_pool.append((column, unique_count))
    if candidate_pool:
        candidate_pool.sort(key=lambda item: item[1])
        return candidate_pool[0][0]
    return columns[0]


def suggest_charts(dataframe: pd.DataFrame) -> list[ChartConfig]:
    charts: list[ChartConfig] = []
    numeric_columns = dataframe.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = dataframe.select_dtypes(exclude=["number"]).columns.tolist()
    category_column = _pick_category_column(dataframe, categorical_columns)

    if category_column and numeric_columns:
        x_key, y_key = category_column, numeric_columns[0]
        charts.append(
            ChartConfig(
                chart_type="bar",
                title=f"Top {x_key} by {y_key}",
                x_key=x_key,
                y_key=y_key,
                description="Summed values grouped by category from the uploaded data.",
                data=_aggregate_for_chart(dataframe, x_key, y_key),
            )
        )

    date_column = next(iter(infer_datetime_columns(dataframe)), None)

    if date_column and numeric_columns:
        temp = dataframe.copy()
        temp[date_column] = pd.to_datetime(temp[date_column], errors="coerce")
        temp = (
            temp.dropna(subset=[date_column])
            .groupby(date_column, as_index=False)[numeric_columns[0]]
            .sum()
            .sort_values(date_column)
            .head(60)
        )
        y_key = numeric_columns[0]
        charts.append(
            ChartConfig(
                chart_type="line",
                title=f"{y_key} over time",
                x_key=date_column,
                y_key=y_key,
                description="Aggregated time-series trend from the uploaded dataset.",
                data=[
                    {date_column: _clean_value(row[date_column]), y_key: _clean_value(row[y_key])}
                    for _, row in temp[[date_column, y_key]].iterrows()
                ],
            )
        )

    if category_column:
        x_key = category_column
        y_key = numeric_columns[0] if numeric_columns else None
        charts.append(
            ChartConfig(
                chart_type="pie",
                title=f"{x_key} share",
                x_key=x_key,
                y_key=y_key or "count",
                description="Top category contribution based on uploaded values.",
                data=_aggregate_for_chart(dataframe, x_key, y_key, limit=6)
                if y_key
                else _aggregate_for_chart(dataframe, x_key, None, limit=6),
            )
        )

    if numeric_columns:
        column = numeric_columns[0]
        series = dataframe[column].dropna()
        bins = min(8, max(4, int(np.sqrt(max(len(series), 1)))))
        counts, edges = np.histogram(series, bins=bins)
        charts.append(
            ChartConfig(
                chart_type="histogram",
                title=f"{column} distribution",
                x_key="range",
                y_key="count",
                description="Frequency distribution for the first numeric column.",
                data=[
                    {
                        "range": f"{round(float(edges[index]), 2)} - {round(float(edges[index + 1]), 2)}",
                        "count": int(counts[index]),
                    }
                    for index in range(len(counts))
                ],
            )
        )

    return charts


def detect_anomalies(dataframe: pd.DataFrame) -> list[str]:
    findings: list[str] = []
    numeric_columns = dataframe.select_dtypes(include=["number"]).columns.tolist()
    for column in numeric_columns[:4]:
        series = dataframe[column].dropna()
        if series.empty:
            continue
        z_scores = (series - series.mean()) / (series.std() or 1)
        outliers = int((z_scores.abs() > 3).sum())
        if outliers:
            findings.append(f"{column} contains {outliers} potential outliers beyond 3 standard deviations.")
    missing = dataframe.isna().sum()
    for column, count in missing[missing > 0].head(3).items():
        findings.append(f"{column} has {int(count)} missing values that may impact analysis quality.")
    return findings[:6]


def build_fallback_ai_insights(profile: dict[str, Any], quick_insights: dict[str, Any]) -> dict[str, Any]:
    summary_parts = [
        f"This dataset contains {profile['row_count']} rows across {profile['column_count']} columns.",
    ]
    if profile["numeric_columns"]:
        summary_parts.append(
            f"It includes {len(profile['numeric_columns'])} numeric fields suitable for trend and variance analysis."
        )
    if profile["categorical_columns"]:
        summary_parts.append(
            f"The categorical structure is led by {', '.join(profile['categorical_columns'][:3])}."
        )
    if quick_insights["top_missing_columns"]:
        top_missing = quick_insights["top_missing_columns"][0]
        summary_parts.append(
            f"The main data-quality concern is missing values in {top_missing['column']}."
        )

    patterns = [
        f"Numeric fields available: {', '.join(profile['numeric_columns'][:5]) or 'none'}.",
        f"Categorical fields available: {', '.join(profile['categorical_columns'][:5]) or 'none'}.",
        f"Strong correlations detected: {len(profile['correlations'])}.",
    ]
    anomalies = quick_insights["anomalies"] or [
        "No major statistical outliers were flagged by the initial local scan."
    ]
    suggestions = [
        "Use the auto-generated charts to compare category performance and identify concentration risks.",
        "Validate missing-value columns before sharing executive conclusions with stakeholders.",
        "Ask targeted AI questions about top segments, seasonal changes, and unusual outliers.",
    ]

    return {
        "summary": " ".join(summary_parts),
        "patterns": patterns,
        "anomalies": anomalies,
        "business_suggestions": suggestions,
        "recommended_questions": [
            "Which categories are driving the strongest results?",
            "Where are the biggest risks or anomalies in this dataset?",
            "What business action should I prioritize from this data?",
        ],
    }


def analyze_dataset(dataframe: pd.DataFrame, file_name: str) -> dict[str, Any]:
    profile = build_profile(dataframe, file_name)
    charts = [chart.model_dump() for chart in suggest_charts(dataframe)]
    quick_insights = {
        "anomalies": detect_anomalies(dataframe),
        "high_correlation_pairs": profile["correlations"][:3],
        "top_missing_columns": profile["missing_values"][:3],
    }

    ai_payload = {
        "profile": profile,
        "quick_insights": quick_insights,
        "chart_titles": [chart["title"] for chart in charts],
    }

    try:
        ai_insights = gemini_service.generate_analysis(ai_payload)
    except Exception:
        ai_insights = build_fallback_ai_insights(profile, quick_insights)

    return {
        "profile": profile,
        "charts": charts,
        "quick_insights": quick_insights,
        "ai_insights": ai_insights,
    }


def chat_with_dataset(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    lower_question = question.lower()
    numeric_columns = dataframe.select_dtypes(include=["number"]).columns.tolist()

    answer = ""
    reasoning = ""
    if "rows" in lower_question or "records" in lower_question:
        answer = f"The dataset contains {len(dataframe)} rows."
        reasoning = "This was calculated directly from the uploaded dataframe length."
    elif "columns" in lower_question:
        answer = f"The dataset contains {len(dataframe.columns)} columns: {', '.join(dataframe.columns)}."
        reasoning = "This is based on the dataframe schema."
    elif ("average" in lower_question or "mean" in lower_question) and numeric_columns:
        target = next((col for col in numeric_columns if col.lower() in lower_question), numeric_columns[0])
        answer = f"The average of {target} is {round(float(dataframe[target].mean()), 2)}."
        reasoning = f"The response uses the numeric column `{target}` and computes its mean."
    elif ("highest" in lower_question or "max" in lower_question) and numeric_columns:
        target = next((col for col in numeric_columns if col.lower() in lower_question), numeric_columns[0])
        answer = f"The maximum value in {target} is {round(float(dataframe[target].max()), 2)}."
        reasoning = f"The response uses the numeric column `{target}` and computes its maximum."
    elif ("lowest" in lower_question or "min" in lower_question) and numeric_columns:
        target = next((col for col in numeric_columns if col.lower() in lower_question), numeric_columns[0])
        answer = f"The minimum value in {target} is {round(float(dataframe[target].min()), 2)}."
        reasoning = f"The response uses the numeric column `{target}` and computes its minimum."

    if answer:
        return {
            "answer": answer,
            "reasoning": reasoning,
            "follow_up": [
                "Show me the main patterns in the data.",
                "Which category contributes the most?",
            ],
        }

    context = {
        "question": question,
        "columns": dataframe.columns.tolist(),
        "row_count": int(len(dataframe)),
        "numeric_summary": dataframe[numeric_columns].describe().fillna(0).round(2).to_dict() if numeric_columns else {},
        "sample_rows": build_preview(dataframe, limit=8),
    }

    try:
        return gemini_service.answer_question(context)
    except Exception:
        return {
            "answer": "I could not fully interpret that question automatically. Try asking about totals, averages, min/max values, row counts, or category distributions.",
            "reasoning": "The local query helper handles common dataset questions, while Gemini handles broader business and exploratory questions.",
            "follow_up": [
                "What are the top 5 categories?",
                "What are the main anomalies in the dataset?",
            ],
        }

