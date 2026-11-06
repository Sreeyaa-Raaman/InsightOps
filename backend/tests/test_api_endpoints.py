import pytest
from app.api.health import health_check
from app.api.datasets import list_all_datasets, get_dataset, get_dataset_preview, get_dataset_overview_api
from app.api.agent import create_session, list_sessions, get_session_history, CreateSessionRequest
from app.api.reports import generate_new_report, list_reports, get_report_detail, GenerateReportRequest
from app.services.dataset_service import DatasetService

def test_health_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert res["app_name"] == "InsightOps"
    assert "active_model" in res

def test_datasets_endpoints():
    datasets = list_all_datasets()
    assert len(datasets) >= 2
    ds_id = datasets[0].id
    
    # Get metadata
    meta = get_dataset(ds_id)
    assert meta["id"] == ds_id
    assert meta["row_count"] > 0
    
    # Get preview
    preview = get_dataset_preview(ds_id, limit=5)
    assert len(preview.rows) <= 5
    assert len(preview.columns) > 0
    
    # Deep overview
    overview = get_dataset_overview_api(ds_id)
    assert overview["status"] == "success"
    assert "row_count" in overview

def test_session_lifecycle():
    datasets = list_all_datasets()
    ds_id = datasets[0].id
    
    sess = create_session(CreateSessionRequest(dataset_id=ds_id, title="Integration Test Session"))
    assert sess.id is not None
    assert sess.title == "Integration Test Session"
    
    sessions = list_sessions()
    ids = [s.id for s in sessions]
    assert sess.id in ids
    
    history = get_session_history(sess.id)
    assert isinstance(history, list)

def test_reports_endpoints():
    datasets = list_all_datasets()
    ds_id = datasets[0].id
    
    req = GenerateReportRequest(dataset_id=ds_id, title="Pytest Executive Report")
    rep = generate_new_report(req)
    assert rep.title == "Pytest Executive Report"
    assert rep.pdf_available is True
    
    all_reps = list_reports()
    assert len(all_reps) >= 1
    
    detail = get_report_detail(rep.id)
    assert detail.id == rep.id
    assert "dimensions" in detail.content
