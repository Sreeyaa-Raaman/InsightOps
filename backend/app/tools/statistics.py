from typing import Any, Dict
import numpy as np
import pandas as pd
from app.tools.base import resolve_column, validate_numeric_column, sanitize_value

def calculate_mean(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate the arithmetic mean of a numeric column."""
    series, err = validate_numeric_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    clean_series = series.dropna()
    if len(clean_series) == 0:
        return {"status": "error", "message": f"Column '{column}' contains no non-null values."}
        
    val = float(clean_series.mean())
    return {
        "status": "success",
        "operation": "mean",
        "column": series.name,
        "mean": round(val, 4),
        "count": len(clean_series)
    }

def calculate_median(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate the median (50th percentile) of a numeric column."""
    series, err = validate_numeric_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    clean_series = series.dropna()
    if len(clean_series) == 0:
        return {"status": "error", "message": f"Column '{column}' contains no non-null values."}
        
    val = float(clean_series.median())
    return {
        "status": "success",
        "operation": "median",
        "column": series.name,
        "median": round(val, 4),
        "count": len(clean_series)
    }

def calculate_mode(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Find the most frequent value(s) in a column (works for numeric or categorical)."""
    matched_col, err = resolve_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    clean_series = df[matched_col].dropna()
    if len(clean_series) == 0:
        return {"status": "error", "message": f"Column '{column}' contains no non-null values."}
        
    mode_series = clean_series.mode()
    modes = [sanitize_value(m) for m in mode_series.tolist()]
    mode_freq = int((clean_series == mode_series.iloc[0]).sum()) if not mode_series.empty else 0
    
    return {
        "status": "success",
        "operation": "mode",
        "column": matched_col,
        "mode_values": modes,
        "frequency": mode_freq,
        "percentage_of_records": round((mode_freq / len(clean_series) * 100), 2)
    }

def calculate_standard_deviation(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate sample standard deviation and variance of a numeric column."""
    series, err = validate_numeric_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    clean_series = series.dropna()
    if len(clean_series) < 2:
        return {"status": "error", "message": f"Column '{column}' requires at least 2 non-null records to compute standard deviation."}
        
    std_val = float(clean_series.std())
    var_val = float(clean_series.var())
    mean_val = float(clean_series.mean())
    cv = (std_val / mean_val * 100) if mean_val != 0 else None
    
    return {
        "status": "success",
        "operation": "standard_deviation",
        "column": series.name,
        "standard_deviation": round(std_val, 4),
        "variance": round(var_val, 4),
        "mean": round(mean_val, 4),
        "coefficient_of_variation_percent": round(cv, 2) if cv is not None else None,
        "sample_size": len(clean_series)
    }

def calculate_min_max(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate min, max, range, and quartiles of a numeric column."""
    series, err = validate_numeric_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    clean_series = series.dropna()
    if len(clean_series) == 0:
        return {"status": "error", "message": f"Column '{column}' contains no non-null records."}
        
    min_val = float(clean_series.min())
    max_val = float(clean_series.max())
    q25 = float(clean_series.quantile(0.25))
    q75 = float(clean_series.quantile(0.75))
    
    return {
        "status": "success",
        "operation": "min_max",
        "column": series.name,
        "min": round(min_val, 4),
        "max": round(max_val, 4),
        "range": round(max_val - min_val, 4),
        "q25": round(q25, 4),
        "q75": round(q75, 4),
        "iqr": round(q75 - q25, 4),
        "count": len(clean_series)
    }

def calculate_correlation(df: pd.DataFrame, column1: str, column2: str) -> Dict[str, Any]:
    """Calculate Pearson correlation coefficient between two numeric columns."""
    s1, err1 = validate_numeric_column(df, column1)
    if err1:
        return {"status": "error", "message": err1}
    s2, err2 = validate_numeric_column(df, column2)
    if err2:
        return {"status": "error", "message": err2}
        
    valid_pair = pd.concat([s1, s2], axis=1).dropna()
    if len(valid_pair) < 3:
        return {"status": "error", "message": "At least 3 complete pairs are required to compute correlation."}
        
    corr = float(valid_pair.iloc[:, 0].corr(valid_pair.iloc[:, 1]))
    if np.isnan(corr):
        return {"status": "error", "message": "Correlation could not be computed (one or both columns may have zero variance)."}
        
    # Interpret strength
    abs_corr = abs(corr)
    if abs_corr >= 0.8:
        strength = "Very strong"
    elif abs_corr >= 0.6:
        strength = "Strong"
    elif abs_corr >= 0.4:
        strength = "Moderate"
    elif abs_corr >= 0.2:
        strength = "Weak"
    else:
        strength = "Very weak / negligible"
        
    direction = "positive" if corr > 0 else "negative" if corr < 0 else "none"
    
    return {
        "status": "success",
        "operation": "correlation",
        "column1": s1.name,
        "column2": s2.name,
        "correlation_coefficient": round(corr, 4),
        "direction": direction,
        "strength": strength,
        "interpretation": f"{strength} {direction} linear relationship between '{s1.name}' and '{s2.name}'.",
        "sample_points": len(valid_pair)
    }
