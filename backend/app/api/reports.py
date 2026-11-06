import io
import csv
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.report_service import ReportService
from app.database.connection import get_db
from app.models.schemas import ReportSummaryItem, ReportDetail

router = APIRouter(prefix="/reports", tags=["Reports"])

class GenerateReportRequest(BaseModel):
    dataset_id: str
    session_id: Optional[str] = None
    title: Optional[str] = None

@router.post("/generate", response_model=ReportDetail)
def generate_new_report(req: GenerateReportRequest):
    """Generate a formal business and data quality report with PDF export."""
    try:
        report = ReportService.generate_report(
            dataset_id=req.dataset_id,
            session_id=req.session_id,
            custom_title=req.title
        )
        return ReportDetail(
            id=report["report_id"],
            session_id=req.session_id,
            dataset_id=req.dataset_id,
            title=report["title"],
            content=report["content"],
            created_at=report["generated_at"],
            pdf_available=report["pdf_available"]
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

@router.get("", response_model=List[ReportSummaryItem])
def list_reports():
    """List all generated reports."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, session_id, dataset_id, title, created_at, pdf_path FROM reports ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            ReportSummaryItem(
                id=r["id"],
                session_id=r["session_id"],
                dataset_id=r["dataset_id"],
                title=r["title"],
                created_at=str(r["created_at"]),
                pdf_available=bool(r["pdf_path"] and Path(r["pdf_path"]).exists())
            )
            for r in rows
        ]

@router.get("/{report_id}", response_model=ReportDetail)
def get_report_detail(report_id: str):
    """Get complete report content and findings."""
    rep = ReportService.get_report(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportDetail(
        id=rep["id"],
        session_id=rep["session_id"],
        dataset_id=rep["dataset_id"],
        title=rep["title"],
        content=rep["content"],
        created_at=rep["created_at"],
        pdf_available=bool(rep.get("pdf_path") and Path(rep["pdf_path"]).exists())
    )

@router.get("/{report_id}/download")
def download_report_pdf(report_id: str):
    """Download the generated report as a publication-ready PDF document."""
    rep = ReportService.get_report(report_id)
    if not rep or not rep.get("pdf_path"):
        raise HTTPException(status_code=404, detail="Report PDF not found")
        
    pdf_path = Path(rep["pdf_path"])
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Report PDF file missing on disk")
        
    safe_name = rep["title"].replace(" ", "_").replace("/", "_") + ".pdf"
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=safe_name
    )

@router.get("/{report_id}/download-csv")
def download_report_csv(report_id: str):
    """Download key numerical metrics and observations as a CSV spreadsheet."""
    rep = ReportService.get_report(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
        
    content = rep.get("content", {})
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Section", "Metric / Column", "Value", "Notes"])
    writer.writerow(["Overview", "Dataset", content.get("dataset_name", ""), ""])
    writer.writerow(["Overview", "Total Rows", content.get("dimensions", {}).get("rows", ""), ""])
    writer.writerow(["Overview", "Total Columns", content.get("dimensions", {}).get("columns", ""), ""])
    writer.writerow(["Overview", "Health Score", content.get("health_score", ""), f"Grade {content.get('health_grade', '')}"])
    
    for col_name, stats in content.get("numeric_metrics", {}).items():
        writer.writerow(["Numeric Metric", col_name, stats.get("total", ""), f"Mean: {stats.get('mean')}, Min: {stats.get('min')}, Max: {stats.get('max')}"])
        
    for issue in content.get("data_quality_issues", []):
        writer.writerow(["Data Quality Issue", issue.get("column", ""), f"{issue.get('count')} ({issue.get('percentage')}%)", issue.get("recommendation", "")])
        
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"}
    )
