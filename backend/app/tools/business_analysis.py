from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from app.tools.base import resolve_column, validate_numeric_column, sanitize_value, sanitize_records

def calculate_total(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate the sum total of a numeric column."""
    series, err = validate_numeric_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    total_val = float(series.sum())
    return {
        "status": "success",
        "operation": "total",
        "column": series.name,
        "total": round(total_val, 2),
        "count": int(series.notna().sum())
    }

def calculate_average(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Calculate the average (mean) of a business metric."""
    series, err = validate_numeric_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    avg_val = float(series.mean())
    return {
        "status": "success",
        "operation": "average",
        "column": series.name,
        "average": round(avg_val, 2),
        "count": int(series.notna().sum())
    }

def group_by_analysis(
    df: pd.DataFrame,
    group_by_column: str,
    metric_column: str,
    aggregation: str = "sum",
    sort_descending: bool = True,
    limit: int = 10
) -> Dict[str, Any]:
    """Group by a categorical column and aggregate a numerical metric."""
    cat_col, err1 = resolve_column(df, group_by_column)
    if err1:
        return {"status": "error", "message": err1}
    metric_series, err2 = validate_numeric_column(df, metric_column)
    if err2:
        return {"status": "error", "message": err2}
        
    agg_clean = aggregation.lower().strip()
    valid_aggs = ["sum", "mean", "count", "min", "max", "median"]
    if agg_clean not in valid_aggs:
        agg_clean = "sum"
        
    temp_df = pd.DataFrame({
        cat_col: df[cat_col],
        metric_series.name: metric_series
    }).dropna()
    
    if len(temp_df) == 0:
        return {"status": "error", "message": "No valid rows found after dropping missing values."}
        
    grouped = temp_df.groupby(cat_col)[metric_series.name].agg(agg_clean).reset_index()
    grouped.columns = [cat_col, f"{metric_series.name}_{agg_clean}"]
    
    grouped = grouped.sort_values(by=f"{metric_series.name}_{agg_clean}", ascending=not sort_descending)
    
    total_metric = float(grouped[f"{metric_series.name}_{agg_clean}"].sum()) if agg_clean == "sum" else None
    
    rows = []
    for _, r in grouped.head(limit).iterrows():
        val = float(r[f"{metric_series.name}_{agg_clean}"])
        share = round((val / total_metric * 100), 2) if total_metric and total_metric > 0 else None
        item = {
            "group": sanitize_value(r[cat_col]),
            "value": round(val, 2),
        }
        if share is not None:
            item["share_percentage"] = share
        rows.append(item)
        
    return {
        "status": "success",
        "operation": f"group_by_{agg_clean}",
        "group_by_column": cat_col,
        "metric_column": metric_series.name,
        "aggregation": agg_clean,
        "total_groups": len(grouped),
        "displayed_groups": len(rows),
        "results": rows
    }

def compare_categories(
    df: pd.DataFrame,
    category_column: str,
    metric_column: str,
    categories_to_compare: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Compare performance metrics between categories."""
    cat_col, err1 = resolve_column(df, category_column)
    if err1:
        return {"status": "error", "message": err1}
    metric_series, err2 = validate_numeric_column(df, metric_column)
    if err2:
        return {"status": "error", "message": err2}
        
    temp_df = pd.DataFrame({
        cat_col: df[cat_col],
        metric_series.name: metric_series
    }).dropna()
    
    grouped = temp_df.groupby(cat_col)[metric_series.name].agg(['count', 'sum', 'mean', 'median', 'min', 'max']).reset_index()
    
    # If specific categories were requested, filter
    if categories_to_compare:
        cats_lower = [str(c).lower().strip() for c in categories_to_compare]
        grouped = grouped[grouped[cat_col].astype(str).str.lower().str.strip().isin(cats_lower)]
        
    grouped = grouped.sort_values(by='sum', ascending=False)
    
    comparisons = []
    overall_sum = float(temp_df[metric_series.name].sum())
    for _, r in grouped.iterrows():
        s = float(r['sum'])
        comparisons.append({
            "category": sanitize_value(r[cat_col]),
            "record_count": int(r['count']),
            "sum": round(s, 2),
            "share_of_total_percent": round((s / overall_sum * 100), 2) if overall_sum > 0 else 0.0,
            "mean": round(float(r['mean']), 2),
            "median": round(float(r['median']), 2),
            "min": round(float(r['min']), 2),
            "max": round(float(r['max']), 2)
        })
        
    return {
        "status": "success",
        "operation": "compare_categories",
        "category_column": cat_col,
        "metric_column": metric_series.name,
        "categories_count": len(comparisons),
        "comparisons": comparisons
    }

def calculate_percentage_change(
    df: pd.DataFrame,
    time_or_index_column: str,
    metric_column: str
) -> Dict[str, Any]:
    """Compute period-over-period percentage change."""
    time_col, err1 = resolve_column(df, time_or_index_column)
    if err1:
        return {"status": "error", "message": err1}
    metric_series, err2 = validate_numeric_column(df, metric_column)
    if err2:
        return {"status": "error", "message": err2}
        
    temp_df = pd.DataFrame({
        time_col: df[time_col],
        metric_series.name: metric_series
    }).dropna()
    
    # If time column is date-like, sort by it
    try:
        temp_df['dt'] = pd.to_datetime(temp_df[time_col])
        temp_df = temp_df.sort_values(by='dt')
        # Aggregate by date if multiple entries per date
        grouped = temp_df.groupby(temp_df['dt'].dt.strftime('%Y-%m-%d'))[metric_series.name].sum().reset_index()
        grouped.columns = [time_col, metric_series.name]
    except Exception:
        # Non-date: group by time_col preserving order
        grouped = temp_df.groupby(time_col, sort=False)[metric_series.name].sum().reset_index()
        
    grouped['pct_change'] = grouped[metric_series.name].pct_change() * 100
    
    history = []
    for _, r in grouped.iterrows():
        val = float(r[metric_series.name])
        pct = float(r['pct_change']) if pd.notna(r['pct_change']) else None
        history.append({
            "period": str(r[time_col]),
            "value": round(val, 2),
            "pct_change": round(pct, 2) if pct is not None else None
        })
        
    return {
        "status": "success",
        "operation": "percentage_change",
        "time_column": time_col,
        "metric_column": metric_series.name,
        "periods_analyzed": len(history),
        "timeline": history[:30] # Return up to 30 periods
    }

def identify_top_performers(
    df: pd.DataFrame,
    entity_column: str,
    metric_column: str,
    limit: int = 5
) -> Dict[str, Any]:
    """Rank top entities by a metric."""
    return group_by_analysis(
        df=df,
        group_by_column=entity_column,
        metric_column=metric_column,
        aggregation="sum",
        sort_descending=True,
        limit=limit
    )

def identify_bottom_performers(
    df: pd.DataFrame,
    entity_column: str,
    metric_column: str,
    limit: int = 5
) -> Dict[str, Any]:
    """Rank lowest performing entities by a metric."""
    return group_by_analysis(
        df=df,
        group_by_column=entity_column,
        metric_column=metric_column,
        aggregation="sum",
        sort_descending=False,
        limit=limit
    )

def detect_outliers(
    df: pd.DataFrame,
    column: str,
    method: str = "iqr",
    threshold: float = 1.5
) -> Dict[str, Any]:
    """Detect statistical outliers in a numeric column using IQR or Z-score."""
    series, err = validate_numeric_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    clean_series = series.dropna()
    total_records = len(clean_series)
    if total_records < 4:
        return {"status": "error", "message": "At least 4 records required for outlier detection."}
        
    method_clean = method.lower().strip()
    if method_clean == "zscore":
        mean = clean_series.mean()
        std = clean_series.std()
        if std == 0:
            return {"status": "success", "outliers_found": 0, "outliers": []}
        z_scores = (clean_series - mean).abs() / std
        outlier_mask = z_scores > threshold
        lower_bound = round(float(mean - threshold * std), 4)
        upper_bound = round(float(mean + threshold * std), 4)
    else:
        # Default to IQR
        q25 = clean_series.quantile(0.25)
        q75 = clean_series.quantile(0.75)
        iqr = q75 - q25
        lower_bound = round(float(q25 - threshold * iqr), 4)
        upper_bound = round(float(q75 + threshold * iqr), 4)
        outlier_mask = (clean_series < lower_bound) | (clean_series > upper_bound)
        
    outliers = clean_series[outlier_mask]
    outlier_count = int(len(outliers))
    
    samples = [round(float(v), 2) for v in outliers.head(10).tolist()]
    
    return {
        "status": "success",
        "operation": f"detect_outliers_{method_clean}",
        "column": series.name,
        "method": method_clean,
        "threshold": threshold,
        "total_records": total_records,
        "outlier_count": outlier_count,
        "outlier_percentage": round((outlier_count / total_records * 100), 2),
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "sample_outliers": samples
    }
