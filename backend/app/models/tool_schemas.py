from typing import Any, Optional, Literal
from pydantic import BaseModel, Field

# Dataset Inspection tool arguments
class ColumnSpecificArgs(BaseModel):
    column: str = Field(..., description="The name of the column in the dataset")

class UniqueValuesArgs(BaseModel):
    column: str = Field(..., description="The name of the column")
    limit: int = Field(20, ge=1, le=100, description="Max unique values to return")

# Statistical Analysis tool arguments
class CorrelationArgs(BaseModel):
    column1: str = Field(..., description="First numeric column")
    column2: str = Field(..., description="Second numeric column")

# Business Analysis tool arguments
class GroupByArgs(BaseModel):
    group_by_column: str = Field(..., description="Column to group by (categorical)")
    metric_column: str = Field(..., description="Column to aggregate (numerical)")
    aggregation: Literal["sum", "mean", "count", "min", "max", "median"] = Field(
        "sum", description="Aggregation method: sum, mean, count, min, max, median"
    )
    sort_descending: bool = Field(True, description="Whether to sort descending")
    limit: int = Field(10, ge=1, le=100, description="Number of grouped rows to return")

class CompareCategoriesArgs(BaseModel):
    category_column: str = Field(..., description="The categorical column to compare")
    metric_column: str = Field(..., description="The numerical metric to compare")
    categories_to_compare: Optional[list[str]] = Field(
        None, description="Optional specific category values to compare; compares top categories if omitted"
    )

class PercentageChangeArgs(BaseModel):
    time_or_index_column: str = Field(..., description="Column representing time, date or sequential order")
    metric_column: str = Field(..., description="Numerical metric to measure percentage change over")

class PerformersArgs(BaseModel):
    entity_column: str = Field(..., description="Entity column (e.g., Product, Region, Store, Customer)")
    metric_column: str = Field(..., description="Metric column (e.g., Revenue, Profit, Quantity, Rating)")
    limit: int = Field(5, ge=1, le=50, description="Number of performers to return")

class DetectOutliersArgs(BaseModel):
    column: str = Field(..., description="Numeric column to detect outliers in")
    method: Literal["iqr", "zscore"] = Field("iqr", description="Method to use: 'iqr' (interquartile range) or 'zscore'")
    threshold: float = Field(1.5, description="Threshold multiplier for outlier boundary (default 1.5 for IQR, 3.0 for z-score)")

# Visualization tool arguments
class BarChartArgs(BaseModel):
    x_column: str = Field(..., description="Categorical column for x-axis")
    y_column: str = Field(..., description="Numerical column for y-axis")
    title: str = Field(..., description="Descriptive chart title")
    limit: int = Field(10, ge=1, le=30, description="Maximum categories to display")
    aggregation: Literal["sum", "mean", "count"] = Field("sum", description="Aggregation for y values")

class LineChartArgs(BaseModel):
    x_column: str = Field(..., description="Date, time or ordered column for x-axis")
    y_column: str = Field(..., description="Numerical column for y-axis")
    title: str = Field(..., description="Descriptive chart title")
    group_by_column: Optional[str] = Field(None, description="Optional secondary category for multi-line comparison")

class PieChartArgs(BaseModel):
    category_column: str = Field(..., description="Categorical column for pie slices")
    metric_column: str = Field(..., description="Numerical column for slice proportions")
    title: str = Field(..., description="Descriptive chart title")
    limit: int = Field(6, ge=2, le=12, description="Maximum slices before grouping into 'Other'")

class HistogramArgs(BaseModel):
    column: str = Field(..., description="Continuous numeric column")
    title: str = Field(..., description="Descriptive chart title")
    bins: int = Field(10, ge=3, le=50, description="Number of histogram bins")

class ScatterPlotArgs(BaseModel):
    x_column: str = Field(..., description="First numeric column for x-axis")
    y_column: str = Field(..., description="Second numeric column for y-axis")
    title: str = Field(..., description="Descriptive chart title")
    color_column: Optional[str] = Field(None, description="Optional categorical column for color encoding")
