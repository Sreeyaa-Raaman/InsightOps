from typing import Any, Dict
import pandas as pd
from app.tools.base import resolve_column, sanitize_value

def get_dataset_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """Inspect dataset shape, memory usage, total missing cells, and duplicate rows."""
    row_count, col_count = df.shape
    total_cells = row_count * col_count
    missing_cells = int(df.isna().sum().sum())
    dup_count = int(df.duplicated().sum())
    
    numeric_cols = list(df.select_dtypes(include=['number']).columns)
    categorical_cols = list(df.select_dtypes(include=['object', 'category', 'string']).columns)
    datetime_cols = list(df.select_dtypes(include=['datetime', 'datetimetz']).columns)
    
    return {
        "status": "success",
        "row_count": row_count,
        "column_count": col_count,
        "total_cells": total_cells,
        "missing_cells": missing_cells,
        "missing_percentage": round((missing_cells / total_cells * 100), 2) if total_cells > 0 else 0.0,
        "duplicate_rows": dup_count,
        "numeric_column_count": len(numeric_cols),
        "categorical_column_count": len(categorical_cols),
        "datetime_column_count": len(datetime_cols),
        "columns": list(df.columns)
    }

def get_column_information(df: pd.DataFrame, column: str = None) -> Dict[str, Any]:
    """Return detailed metadata for all columns or a specific column."""
    if column:
        matched_col, err = resolve_column(df, column)
        if err:
            return {"status": "error", "message": err}
        target_cols = [matched_col]
    else:
        target_cols = list(df.columns)
        
    col_details = []
    for col in target_cols:
        series = df[col]
        non_null = int(series.notna().sum())
        null_count = int(series.isna().sum())
        unique_cnt = int(series.nunique(dropna=True))
        
        # Sample non-null values
        samples = [sanitize_value(v) for v in series.dropna().unique()[:5]]
        
        col_details.append({
            "name": str(col),
            "dtype": str(series.dtype),
            "non_null_count": non_null,
            "null_count": null_count,
            "null_percentage": round((null_count / len(df) * 100), 2) if len(df) > 0 else 0.0,
            "unique_count": unique_cnt,
            "sample_values": samples
        })
        
    return {
        "status": "success",
        "total_columns": len(target_cols),
        "column_details": col_details
    }

def get_data_types(df: pd.DataFrame) -> Dict[str, Any]:
    """Return the detected data types for all columns."""
    dtypes = {str(c): str(df[c].dtype) for c in df.columns}
    type_breakdown = {}
    for dt in dtypes.values():
        type_breakdown[dt] = type_breakdown.get(dt, 0) + 1
        
    return {
        "status": "success",
        "column_data_types": dtypes,
        "summary": type_breakdown
    }

def get_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze missing/null records across all columns."""
    missing_series = df.isna().sum()
    cols_with_missing = {}
    total_rows = len(df)
    
    for col, count in missing_series.items():
        if count > 0:
            cols_with_missing[str(col)] = {
                "missing_count": int(count),
                "missing_percentage": round((count / total_rows * 100), 2) if total_rows > 0 else 0.0
            }
            
    return {
        "status": "success",
        "has_missing_values": len(cols_with_missing) > 0,
        "total_missing_cells": int(missing_series.sum()),
        "columns_with_missing_count": len(cols_with_missing),
        "missing_by_column": cols_with_missing
    }

def get_duplicate_records(df: pd.DataFrame) -> Dict[str, Any]:
    """Identify duplicate rows in the dataset."""
    dup_mask = df.duplicated()
    dup_count = int(dup_mask.sum())
    
    sample_duplicates = []
    if dup_count > 0:
        sample_df = df[dup_mask].head(5)
        for _, row in sample_df.iterrows():
            sample_duplicates.append({str(k): sanitize_value(v) for k, v in row.items()})
            
    return {
        "status": "success",
        "duplicate_count": dup_count,
        "duplicate_percentage": round((dup_count / len(df) * 100), 2) if len(df) > 0 else 0.0,
        "sample_duplicates": sample_duplicates
    }

def get_unique_values(df: pd.DataFrame, column: str, limit: int = 20) -> Dict[str, Any]:
    """Retrieve distinct unique values and their frequencies for a column."""
    matched_col, err = resolve_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    series = df[matched_col].dropna()
    total_unique = int(series.nunique())
    val_counts = series.value_counts().head(limit)
    
    values_with_count = [
        {"value": sanitize_value(val), "count": int(cnt), "percentage": round((cnt / len(df) * 100), 2)}
        for val, cnt in val_counts.items()
    ]
    
    return {
        "status": "success",
        "column": matched_col,
        "total_unique_values": total_unique,
        "displayed_values_count": len(values_with_count),
        "frequencies": values_with_count
    }
