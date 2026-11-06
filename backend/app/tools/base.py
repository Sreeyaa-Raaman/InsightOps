import difflib
from typing import Any, Tuple, Optional
import numpy as np
import pandas as pd

def sanitize_value(val: Any) -> Any:
    """Convert numpy / pandas types and NaN / Inf to JSON-serializable Python values."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32)):
        if np.isnan(val) or np.isinf(val):
            return None
        return float(round(val, 4))
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return str(val)
    return val

def sanitize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{k: sanitize_value(v) for k, v in row.items()} for row in records]

def resolve_column(df: pd.DataFrame, col_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Case-insensitive / fuzzy column resolution.
    Returns (matched_col_name, error_message).
    """
    if not col_name:
        return None, "No column name provided."
    
    # Exact match
    if col_name in df.columns:
        return col_name, None
        
    # Case-insensitive match
    lower_map = {str(c).lower().strip(): c for c in df.columns}
    target_clean = col_name.lower().strip()
    if target_clean in lower_map:
        return lower_map[target_clean], None
        
    # Match without underscores or spaces
    norm_map = {str(c).lower().replace(" ", "").replace("_", ""): c for c in df.columns}
    target_norm = target_clean.replace(" ", "").replace("_", "")
    if target_norm in norm_map:
        return norm_map[target_norm], None
        
    # Close match with difflib
    close_matches = difflib.get_close_matches(col_name, [str(c) for c in df.columns], n=1, cutoff=0.7)
    if close_matches:
        return close_matches[0], None
        
    return None, f"Column '{col_name}' not found. Available columns in dataset: {list(df.columns)}"

def validate_numeric_column(df: pd.DataFrame, col_name: str) -> Tuple[Optional[pd.Series], Optional[str]]:
    """Resolve column and ensure it is or can be coerced to numeric."""
    matched_col, err = resolve_column(df, col_name)
    if err:
        return None, err
        
    series = df[matched_col]
    if not pd.api.types.is_numeric_dtype(series):
        # Attempt coercion if possible
        coerced = pd.to_numeric(series, errors='coerce')
        if coerced.notna().sum() > 0:
            return coerced, None
        return None, f"Column '{matched_col}' is non-numeric (dtype: {series.dtype}). This statistical operation requires a numeric column."
        
    return series, None
