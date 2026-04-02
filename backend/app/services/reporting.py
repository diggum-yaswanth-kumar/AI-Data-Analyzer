from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import get_settings


def generate_report(dataset_id: str, file_name: str, analysis: dict) -> Path:
    settings = get_settings()
    output_path = settings.report_dir / f"{dataset_id}.pdf"
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#D7E6FF"),
        )
    )
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)

    story = [
        Paragraph("Data Insight AI Report", styles["Title"]),
        Spacer(1, 10),
        Paragraph(f"Dataset: {file_name}", styles["Heading3"]),
        Spacer(1, 14),
        Paragraph(analysis["ai_insights"]["summary"], styles["BodySmall"]),
        Spacer(1, 12),
        Paragraph("Dataset Overview", styles["Heading2"]),
    ]

    profile = analysis["profile"]
    overview = Table(
        [
            ["Rows", str(profile["row_count"])],
            ["Columns", str(profile["column_count"])],
            ["Numeric Columns", ", ".join(profile["numeric_columns"]) or "None"],
            ["Categorical Columns", ", ".join(profile["categorical_columns"]) or "None"],
        ],
        colWidths=[130, 360],
    )
    overview.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2A44")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.whitesmoke),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([overview, Spacer(1, 14), Paragraph("AI Insights", styles["Heading2"])])

    for section_name in ["patterns", "anomalies", "business_suggestions"]:
        story.append(Paragraph(section_name.replace("_", " ").title(), styles["Heading3"]))
        for item in analysis["ai_insights"].get(section_name, []):
            story.append(Paragraph(f"- {item}", styles["BodySmall"]))
        story.append(Spacer(1, 8))

    if analysis["charts"]:
        story.append(Paragraph("Recommended Visuals", styles["Heading2"]))
        chart_rows = [["Chart", "Description"]]
        chart_rows.extend([[chart["title"], chart["description"]] for chart in analysis["charts"]])
        chart_table = Table(chart_rows, colWidths=[180, 310])
        chart_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D4ED8")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#111827")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(chart_table)

    doc.build(story)
    return output_path
