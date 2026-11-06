from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from app.tools.base import resolve_column, validate_numeric_column, sanitize_value

def generate_bar_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    limit: int = 10,
    aggregation: str = "sum"
) -> Dict[str, Any]:
    """Generate structured configuration and data points for a bar chart."""
    x_col, err1 = resolve_column(df, x_column)
    if err1:
        return {"status": "error", "message": err1}
    y_series, err2 = validate_numeric_column(df, y_column)
    if err2:
        return {"status": "error", "message": err2}
        
    agg = aggregation.lower().strip()
    if agg not in ["sum", "mean", "count"]:
        agg = "sum"
        
    temp_df = pd.DataFrame({
        x_col: df[x_col],
        y_series.name: y_series
    }).dropna()
    
    grouped = temp_df.groupby(x_col)[y_series.name].agg(agg).reset_index()
    grouped.columns = [x_col, y_series.name]
    grouped = grouped.sort_values(by=y_series.name, ascending=False).head(limit)
    
    chart_data = []
    for _, r in grouped.iterrows():
        chart_data.append({
            x_col: str(r[x_col]),
            y_series.name: round(float(r[y_series.name]), 2)
        })
        
    chart_config = {
        "chart_type": "bar",
        "title": title or f"{y_series.name} by {x_col}",
        "x_key": x_col,
        "y_keys": [y_series.name],
        "data": chart_data,
        "x_label": x_col,
        "y_label": f"{y_series.name} ({agg})",
        "description": f"Bar chart showing {y_series.name} across top {len(chart_data)} {x_col} categories."
    }
    
    return {
        "status": "success",
        "operation": "generate_bar_chart",
        "chart_config": chart_config
    }

def generate_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    group_by_column: Optional[str] = None
) -> Dict[str, Any]:
    """Generate structured configuration for a time series or sequential line chart."""
    x_col, err1 = resolve_column(df, x_column)
    if err1:
        return {"status": "error", "message": err1}
    y_series, err2 = validate_numeric_column(df, y_column)
    if err2:
        return {"status": "error", "message": err2}
        
    temp_df = pd.DataFrame({
        x_col: df[x_col],
        y_series.name: y_series
    })
    
    # Check for date conversion
    try:
        temp_df['dt'] = pd.to_datetime(temp_df[x_col])
        temp_df['formatted_x'] = temp_df['dt'].dt.strftime('%Y-%m-%d')
        x_sort_key = 'dt'
        x_display_col = 'formatted_x'
    except Exception:
        temp_df['formatted_x'] = temp_df[x_col].astype(str)
        x_sort_key = 'formatted_x'
        x_display_col = 'formatted_x'
        
    if group_by_column:
        grp_col, g_err = resolve_column(df, group_by_column)
        if not g_err:
            temp_df[grp_col] = df[grp_col]
            # Top 4 groups to keep chart clean
            top_groups = temp_df[grp_col].value_counts().head(4).index.tolist()
            filtered_df = temp_df[temp_df[grp_col].isin(top_groups)]
            pivot = filtered_df.pivot_table(index=x_display_col, columns=grp_col, values=y_series.name, aggfunc='sum').fillna(0)
            
            data_points = []
            for idx_val, row in pivot.iterrows():
                dp = {x_col: str(idx_val)}
                for col_name in pivot.columns:
                    dp[str(col_name)] = round(float(row[col_name]), 2)
                data_points.append(dp)
                
            return {
                "status": "success",
                "operation": "generate_line_chart",
                "chart_config": {
                    "chart_type": "line",
                    "title": title or f"{y_series.name} over {x_col} by {grp_col}",
                    "x_key": x_col,
                    "y_keys": [str(c) for c in pivot.columns],
                    "data": data_points[:40],
                    "x_label": x_col,
                    "y_label": y_series.name,
                    "description": f"Multi-line chart of {y_series.name} across {grp_col}."
                }
            }
            
    # Single series line chart
    grouped = temp_df.groupby(x_display_col)[y_series.name].sum().reset_index()
    grouped.columns = [x_col, y_series.name]
    
    data_points = [
        {x_col: str(r[x_col]), y_series.name: round(float(r[y_series.name]), 2)}
        for _, r in grouped.iterrows()
    ]
    
    chart_config = {
        "chart_type": "line",
        "title": title or f"{y_series.name} over {x_col}",
        "x_key": x_col,
        "y_keys": [y_series.name],
        "data": data_points[:40],
        "x_label": x_col,
        "y_label": y_series.name,
        "description": f"Line chart of {y_series.name} over {x_col}."
    }
    
    return {
        "status": "success",
        "operation": "generate_line_chart",
        "chart_config": chart_config
    }

def generate_pie_chart(
    df: pd.DataFrame,
    category_column: str,
    metric_column: str,
    title: str,
    limit: int = 6
) -> Dict[str, Any]:
    """Generate structured configuration for a pie / donut chart."""
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
    
    grouped = temp_df.groupby(cat_col)[metric_series.name].sum().reset_index()
    grouped = grouped.sort_values(by=metric_series.name, ascending=False)
    
    total_val = float(grouped[metric_series.name].sum())
    top_slices = grouped.head(limit)
    other_slices = grouped.iloc[limit:]
    
    slices = []
    for _, r in top_slices.iterrows():
        val = float(r[metric_series.name])
        slices.append({
            "name": str(r[cat_col]),
            "value": round(val, 2),
            "percentage": round((val / total_val * 100), 2) if total_val > 0 else 0
        })
        
    if not other_slices.empty:
        other_val = float(other_slices[metric_series.name].sum())
        slices.append({
            "name": "Other",
            "value": round(other_val, 2),
            "percentage": round((other_val / total_val * 100), 2) if total_val > 0 else 0
        })
        
    chart_config = {
        "chart_type": "pie",
        "title": title or f"Share of {metric_series.name} by {cat_col}",
        "x_key": "name",
        "y_keys": ["value"],
        "data": slices,
        "x_label": cat_col,
        "y_label": metric_series.name,
        "description": f"Pie chart showing proportion of {metric_series.name} across {cat_col}."
    }
    
    return {
        "status": "success",
        "operation": "generate_pie_chart",
        "chart_config": chart_config
    }

def generate_histogram(
    df: pd.DataFrame,
    column: str,
    title: str,
    bins: int = 10
) -> Dict[str, Any]:
    """Generate frequency bins for numeric distribution histograms."""
    series, err = validate_numeric_column(df, column)
    if err:
        return {"status": "error", "message": err}
        
    clean_series = series.dropna()
    if len(clean_series) < 3:
        return {"status": "error", "message": "At least 3 values required to plot histogram."}
        
    counts, bin_edges = np.histogram(clean_series, bins=bins)
    
    data = []
    for i in range(len(counts)):
        bin_label = f"{bin_edges[i]:.1f} - {bin_edges[i+1]:.1f}"
        data.append({
            "bin": bin_label,
            "frequency": int(counts[i])
        })
        
    chart_config = {
        "chart_type": "bar",
        "title": title or f"Distribution of {series.name}",
        "x_key": "bin",
        "y_keys": ["frequency"],
        "data": data,
        "x_label": f"{series.name} Range",
        "y_label": "Frequency",
        "description": f"Histogram showing frequency distribution of {series.name} across {bins} bins."
    }
    
    return {
        "status": "success",
        "operation": "generate_histogram",
        "chart_config": chart_config
    }

def generate_scatter_plot(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    color_column: Optional[str] = None
) -> Dict[str, Any]:
    """Generate scatter plot points for bivariate relationship analysis."""
    x_series, err1 = validate_numeric_column(df, x_column)
    if err1:
        return {"status": "error", "message": err1}
    y_series, err2 = validate_numeric_column(df, y_column)
    if err2:
        return {"status": "error", "message": err2}
        
    cols_to_keep = [x_series.name, y_series.name]
    color_col_resolved = None
    if color_column:
        resolved, _ = resolve_column(df, color_column)
        if resolved:
            color_col_resolved = resolved
            cols_to_keep.append(resolved)
            
    temp_df = df[cols_to_keep].dropna()
    
    # Sample down to 80 points if large to keep browser rendering lightweight and crisp
    if len(temp_df) > 80:
        temp_df = temp_df.sample(80, random_state=42)
        
    data = []
    for _, r in temp_df.iterrows():
        dp = {
            x_series.name: round(float(r[x_series.name]), 2),
            y_series.name: round(float(r[y_series.name]), 2)
        }
        if color_col_resolved:
            dp[color_col_resolved] = str(r[color_col_resolved])
        data.append(dp)
        
    chart_config = {
        "chart_type": "scatter",
        "title": title or f"{y_series.name} vs. {x_series.name}",
        "x_key": x_series.name,
        "y_keys": [y_series.name],
        "data": data,
        "x_label": x_series.name,
        "y_label": y_series.name,
        "description": f"Scatter plot of {y_series.name} versus {x_series.name} ({len(data)} sample points)."
    }
    
    return {
        "status": "success",
        "operation": "generate_scatter_plot",
        "chart_config": chart_config
    }
