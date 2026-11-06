import os
import uuid
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from fastapi import UploadFile

from app.config import settings
from app.database.connection import get_db
from app.models.schemas import DatasetOverview, ColumnInfo, DatasetListItem, DatasetPreviewResponse
from app.tools.base import sanitize_value

class DatasetService:
    _df_cache: Dict[str, pd.DataFrame] = {}

    @classmethod
    def load_df(cls, file_path: str) -> pd.DataFrame:
        """Load DataFrame handling CSV encoding variations and Excel formats."""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
            
        # Try UTF-8 first, fallback to common encodings
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
        last_error = None
        for enc in encodings:
            try:
                return pd.read_csv(file_path, encoding=enc)
            except Exception as e:
                last_error = e
                continue
                
        raise ValueError(f"Unable to read CSV file with standard encodings: {str(last_error)}")

    @classmethod
    def get_dataset_df(cls, dataset_id: str) -> pd.DataFrame:
        """Get cached DataFrame or load from disk."""
        if dataset_id in cls._df_cache:
            return cls._df_cache[dataset_id]
            
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM datasets WHERE id = ?", (dataset_id,))
            row = cursor.fetchone()
            if not row:
                raise FileNotFoundError(f"Dataset '{dataset_id}' not found.")
                
            df = cls.load_df(row["file_path"])
            cls._df_cache[dataset_id] = df
            return df

    @classmethod
    def get_dataset_metadata(cls, dataset_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
            row = cursor.fetchone()
            if not row:
                return None
                
            cols = json.loads(row["columns_json"]) if row.get("columns_json") else []
            return {
                "id": row["id"],
                "filename": row["filename"],
                "original_name": row["original_name"],
                "file_size_bytes": row["file_size_bytes"],
                "row_count": row["row_count"],
                "column_count": row["column_count"],
                "columns": cols,
                "created_at": str(row["created_at"])
            }

    @classmethod
    def inspect_dataframe(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract column metadata including dtypes, counts, and samples."""
        columns_meta = []
        for col in df.columns:
            series = df[col]
            samples = [sanitize_value(v) for v in series.dropna().unique()[:3]]
            columns_meta.append({
                "name": str(col),
                "dtype": str(series.dtype),
                "non_null_count": int(series.notna().sum()),
                "null_count": int(series.isna().sum()),
                "unique_count": int(series.nunique(dropna=True)),
                "sample_values": samples
            })
        return columns_meta

    @classmethod
    async def save_uploaded_file(cls, file: UploadFile) -> DatasetOverview:
        # 1. Validate file extension
        orig_name = Path(file.filename or "dataset.csv").name
        ext = Path(orig_name).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}")

        # 2. Prevent path traversal and generate secure filename
        dataset_id = str(uuid.uuid4())
        safe_filename = f"{dataset_id}{ext}"
        target_path = settings.DATASETS_DIR / safe_filename

        # 3. Read and check file size
        contents = await file.read()
        file_size = len(contents)
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise ValueError(f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB.")
        if file_size == 0:
            raise ValueError("Uploaded file is empty.")

        with open(target_path, "wb") as f:
            f.write(contents)

        # 4. Load and inspect DataFrame
        try:
            df = cls.load_df(str(target_path))
        except Exception as e:
            if target_path.exists():
                target_path.unlink()
            raise ValueError(f"Failed to parse dataset: {str(e)}")

        if df.empty:
            if target_path.exists():
                target_path.unlink()
            raise ValueError("The uploaded dataset contains zero rows.")

        # Clean duplicate column names
        df.columns = [str(c).strip() for c in df.columns]
        row_count, col_count = df.shape
        columns_meta = cls.inspect_dataframe(df)

        # 5. Persist to SQLite
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO datasets (id, filename, original_name, file_path, file_size_bytes, row_count, column_count, columns_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    safe_filename,
                    orig_name,
                    str(target_path),
                    file_size,
                    row_count,
                    col_count,
                    json.dumps(columns_meta)
                )
            )

        # Cache in memory
        cls._df_cache[dataset_id] = df

        return DatasetOverview(
            id=dataset_id,
            filename=safe_filename,
            original_name=orig_name,
            file_size_bytes=file_size,
            row_count=row_count,
            column_count=col_count,
            columns=[ColumnInfo(**c) for c in columns_meta],
            created_at="just now"
        )

    @classmethod
    def list_datasets(cls) -> List[DatasetListItem]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, original_name, row_count, column_count, file_size_bytes, created_at FROM datasets ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            return [
                DatasetListItem(
                    id=r["id"],
                    original_name=r["original_name"],
                    row_count=r["row_count"],
                    column_count=r["column_count"],
                    file_size_bytes=r["file_size_bytes"],
                    created_at=str(r["created_at"])
                )
                for r in rows
            ]

    @classmethod
    def get_preview(cls, dataset_id: str, limit: int = 15) -> DatasetPreviewResponse:
        df = cls.get_dataset_df(dataset_id)
        meta = cls.get_dataset_metadata(dataset_id)
        if not meta:
            raise FileNotFoundError("Dataset not found")
            
        sample_df = df.head(limit)
        rows = []
        for _, r in sample_df.iterrows():
            row_dict = {str(k): sanitize_value(v) for k, v in r.items()}
            rows.append(row_dict)
            
        dtypes = {str(c): str(df[c].dtype) for c in df.columns}
        
        return DatasetPreviewResponse(
            id=dataset_id,
            original_name=meta["original_name"],
            total_rows=len(df),
            total_columns=len(df.columns),
            columns=[str(c) for c in df.columns],
            dtypes=dtypes,
            rows=rows
        )

    @classmethod
    def seed_sample_datasets_if_needed(cls):
        """Seed ecommerce_sales.csv and supermarket_sales.csv if not already registered."""
        sample_paths = [
            Path("sample_data/ecommerce_sales.csv"),
            Path("sample_data/supermarket_sales.csv")
        ]
        
        with get_db() as conn:
            cursor = conn.cursor()
            for sp in sample_paths:
                if not sp.exists():
                    continue
                cursor.execute("SELECT id FROM datasets WHERE original_name = ?", (sp.name,))
                if cursor.fetchone():
                    continue
                    
                dataset_id = str(uuid.uuid4())
                safe_name = f"{dataset_id}{sp.suffix}"
                target_path = settings.DATASETS_DIR / safe_name
                shutil.copy(sp, target_path)
                
                df = cls.load_df(str(target_path))
                row_count, col_count = df.shape
                cols_meta = cls.inspect_dataframe(df)
                file_size = sp.stat().st_size
                
                cursor.execute(
                    """
                    INSERT INTO datasets (id, filename, original_name, file_path, file_size_bytes, row_count, column_count, columns_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        dataset_id,
                        safe_name,
                        sp.name,
                        str(target_path),
                        file_size,
                        row_count,
                        col_count,
                        json.dumps(cols_meta)
                    )
                )
                print(f"[DatasetService] Seeded sample dataset: {sp.name} ({dataset_id})")
