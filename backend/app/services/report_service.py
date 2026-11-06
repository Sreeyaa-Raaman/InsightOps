import uuid
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.config import settings
from app.database.connection import get_db
from app.services.dataset_service import DatasetService
from app.tools.reporting import generate_summary_report, generate_data_quality_report

class ReportService:
    @classmethod
    def generate_report(
        cls,
        dataset_id: str,
        session_id: Optional[str] = None,
        custom_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate analysis report JSON and render downloadable PDF."""
        df = DatasetService.get_dataset_df(dataset_id)
        meta = DatasetService.get_dataset_metadata(dataset_id)
        if not meta:
            raise FileNotFoundError(f"Dataset {dataset_id} not found")

        report_id = str(uuid.uuid4())
        title = custom_title or f"Executive Analysis Report - {meta['original_name']}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Compute summary & quality findings using verified Python tools
        summary_res = generate_summary_report(df)
        quality_res = generate_data_quality_report(df)

        # 2. Gather conversation highlights if session provided
        session_highlights = []
        if session_id:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                    (session_id,)
                )
                rows = cursor.fetchall()
                for r in rows:
                    if r["role"] == "user":
                        session_highlights.append(f"Q: {r['content']}")

        # 3. Compile report content
        report_content = {
            "title": title,
            "dataset_name": meta["original_name"],
            "generated_at": timestamp,
            "dimensions": {"rows": meta["row_count"], "columns": meta["column_count"]},
            "health_score": quality_res.get("data_health_score"),
            "health_grade": quality_res.get("health_grade"),
            "numeric_metrics": summary_res.get("numeric_metrics_summary", {}),
            "categorical_dimensions": summary_res.get("categorical_dimensions_summary", {}),
            "data_quality_issues": quality_res.get("issues_breakdown", []),
            "analysis_questions": session_highlights,
            "recommendations": [
                f"Dataset exhibits {quality_res.get('health_grade')} grade health ({quality_res.get('data_health_score')}/100).",
                f"Ensure periodic validation of columns with missing data ({len(quality_res.get('issues_breakdown', []))} issues identified).",
                "Leverage high-performing categorical drivers for targeted revenue initiatives."
            ]
        }

        # 4. Render PDF using ReportLab
        pdf_filename = f"{report_id}.pdf"
        pdf_path = settings.REPORTS_DIR / pdf_filename
        cls._render_pdf(report_content, str(pdf_path))

        # 5. Store in SQLite
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO reports (id, session_id, dataset_id, title, content_json, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (report_id, session_id, dataset_id, title, json.dumps(report_content), str(pdf_path))
            )

        return {
            "report_id": report_id,
            "title": title,
            "dataset_id": dataset_id,
            "pdf_available": True,
            "generated_at": timestamp,
            "content": report_content
        }

    @classmethod
    def _render_pdf(cls, content: Dict[str, Any], output_path: str):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=10
        )
        sub_style = ParagraphStyle(
            'ReportSub',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#334155')
        )

        elements = []

        # Header
        elements.append(Paragraph(content["title"], title_style))
        elements.append(Paragraph(f"Dataset: <b>{content['dataset_name']}</b> | Generated: {content['generated_at']} | Health Score: <b>{content['health_score']}/100 (Grade {content['health_grade']})</b>", sub_style))
        elements.append(Spacer(1, 10))

        # Dataset Overview Table
        elements.append(Paragraph("1. Dataset Overview", h2_style))
        overview_data = [
            ["Attribute", "Value"],
            ["Total Records", f"{content['dimensions']['rows']:,}"],
            ["Total Attributes", str(content['dimensions']['columns'])],
            ["Data Hygiene Grade", f"{content['health_grade']} ({content['health_score']}%)"],
            ["Identified Issues", str(len(content['data_quality_issues']))]
        ]
        t = Table(overview_data, colWidths=[200, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

        # Numeric Metrics Summary
        if content.get("numeric_metrics"):
            elements.append(Paragraph("2. Numeric Metrics Summary", h2_style))
            num_table = [["Metric Column", "Mean", "Median", "Min", "Max", "Total"]]
            for col_name, stats in list(content["numeric_metrics"].items())[:8]:
                num_table.append([
                    col_name,
                    f"{stats.get('mean'):,}",
                    f"{stats.get('median'):,}",
                    f"{stats.get('min'):,}",
                    f"{stats.get('max'):,}",
                    f"{stats.get('total'):,}"
                ])
            nt = Table(num_table, colWidths=[130, 75, 75, 75, 75, 90])
            nt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ]))
            elements.append(nt)
            elements.append(Spacer(1, 10))

        # Recommendations
        elements.append(Paragraph("3. Strategic Recommendations", h2_style))
        for rec in content.get("recommendations", []):
            elements.append(Paragraph(f"• {rec}", body_style))
            elements.append(Spacer(1, 3))

        doc.build(elements)

    @classmethod
    def get_report(cls, report_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "session_id": row["session_id"],
                "dataset_id": row["dataset_id"],
                "title": row["title"],
                "content": json.loads(row["content_json"]),
                "pdf_path": row["pdf_path"],
                "created_at": str(row["created_at"])
            }
