from typing import Any, Dict
import pandas as pd
from app.tools.base import sanitize_value

def generate_summary_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a comprehensive executive statistical and business summary report."""
    row_count, col_count = df.shape
    numeric_cols = list(df.select_dtypes(include=['number']).columns)
    cat_cols = list(df.select_dtypes(include=['object', 'category', 'string']).columns)
    
    num_summaries = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) > 0:
            num_summaries[str(col)] = {
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
                "median": round(float(series.median()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "total": round(float(series.sum()), 2)
            }
            
    cat_summaries = {}
    for col in cat_cols:
        series = df[col].dropna()
        if len(series) > 0:
            top_val = series.mode().iloc[0] if not series.empty else None
            cat_summaries[str(col)] = {
                "unique_count": int(series.nunique()),
                "top_value": sanitize_value(top_val),
                "top_value_frequency": int((series == top_val).sum()) if top_val is not None else 0
            }
            
    return {
        "status": "success",
        "operation": "generate_summary_report",
        "dataset_dimensions": {"rows": row_count, "columns": col_count},
        "numeric_metrics_summary": num_summaries,
        "categorical_dimensions_summary": cat_summaries,
        "insights_summary": f"Dataset contains {row_count:,} observations across {col_count} attributes ({len(numeric_cols)} numeric, {len(cat_cols)} categorical)."
    }

def generate_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a data hygiene, completeness, uniqueness, and consistency report."""
    row_count, col_count = df.shape
    total_cells = row_count * col_count
    
    missing_by_col = df.isna().sum()
    duplicate_rows = int(df.duplicated().sum())
    
    quality_issues = []
    
    # Missing value checks
    for col, count in missing_by_col.items():
        if count > 0:
            pct = round((count / row_count * 100), 2)
            severity = "High" if pct > 20 else "Medium" if pct > 5 else "Low"
            quality_issues.append({
                "column": str(col),
                "type": "Missing Values",
                "count": int(count),
                "percentage": pct,
                "severity": severity,
                "recommendation": f"Impute or investigate missing values in '{col}' ({pct}% missing)."
            })
            
    # Duplicate rows check
    if duplicate_rows > 0:
        dup_pct = round((duplicate_rows / row_count * 100), 2)
        quality_issues.append({
            "column": "Entire Record",
            "type": "Duplicate Rows",
            "count": duplicate_rows,
            "percentage": dup_pct,
            "severity": "Medium" if dup_pct > 1 else "Low",
            "recommendation": f"Deduplicate {duplicate_rows} redundant rows to prevent biased aggregates."
        })
        
    # Constant columns check (0 variance)
    for col in df.columns:
        if df[col].nunique(dropna=False) <= 1:
            quality_issues.append({
                "column": str(col),
                "type": "Constant Column",
                "count": row_count,
                "percentage": 100.0,
                "severity": "Low",
                "recommendation": f"Column '{col}' has only one unique value; consider dropping for analysis."
            })
            
    # Calculate Data Health Score (0 - 100)
    missing_penalty = min(40, (df.isna().sum().sum() / total_cells * 100) * 2) if total_cells > 0 else 0
    duplicate_penalty = min(20, (duplicate_rows / row_count * 100) * 5) if row_count > 0 else 0
    health_score = max(0, round(100 - missing_penalty - duplicate_penalty, 1))
    
    return {
        "status": "success",
        "operation": "generate_data_quality_report",
        "data_health_score": health_score,
        "health_grade": "A" if health_score >= 90 else "B" if health_score >= 75 else "C" if health_score >= 60 else "D",
        "total_rows": row_count,
        "total_columns": col_count,
        "total_missing_cells": int(missing_by_col.sum()),
        "duplicate_rows": duplicate_rows,
        "issues_detected": len(quality_issues),
        "issues_breakdown": quality_issues
    }
