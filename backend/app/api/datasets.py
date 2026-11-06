from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.dataset_service import DatasetService
from app.models.schemas import DatasetOverview, DatasetListItem, DatasetPreviewResponse

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=DatasetOverview, status_code=201)
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a new CSV or Excel dataset, inspect its schema and store it safely."""
    try:
        overview = await DatasetService.save_uploaded_file(file)
        return overview
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal upload error: {str(e)}")

@router.get("", response_model=List[DatasetListItem])
def list_all_datasets():
    """List all uploaded datasets with record counts and file sizes."""
    return DatasetService.list_datasets()

@router.get("/{dataset_id}", response_model=DatasetOverview)
def get_dataset(dataset_id: str):
    """Get metadata and column schema for a specific dataset."""
    meta = DatasetService.get_dataset_metadata(dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return meta

@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def get_dataset_preview(dataset_id: str, limit: int = Query(15, ge=1, le=100)):
    """Preview the first 10-20 records of the dataset with data types."""
    try:
        return DatasetService.get_preview(dataset_id, limit=limit)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")

@router.get("/{dataset_id}/overview")
def get_dataset_overview_api(dataset_id: str):
    """Retrieve deep statistical and data quality overview for the dataset."""
    try:
        df = DatasetService.get_dataset_df(dataset_id)
        from app.tools.inspection import get_dataset_overview
        return get_dataset_overview(df)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
