from typing import Any, Optional
from pydantic import BaseModel, Field

# Dataset models
class ColumnInfo(BaseModel):
    name: str
    dtype: str
    non_null_count: int
    null_count: int
    unique_count: int
    sample_values: list[Any] = []

class DatasetOverview(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size_bytes: int
    row_count: int
    column_count: int
    columns: list[ColumnInfo]
    created_at: str

class DatasetListItem(BaseModel):
    id: str
    original_name: str
    row_count: int
    column_count: int
    file_size_bytes: int
    created_at: str

class DatasetPreviewResponse(BaseModel):
    id: str
    original_name: str
    total_rows: int
    total_columns: int
    columns: list[str]
    dtypes: dict[str, str]
    rows: list[dict[str, Any]]

# Agent and Chat models
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    dataset_id: str
    message: str

class ToolExecutionTraceItem(BaseModel):
    tool_name: str
    description: str
    parameters: dict[str, Any]
    status: str
    summary: str

class ChartConfig(BaseModel):
    chart_type: str = Field(description="bar, line, pie, histogram, scatter")
    title: str
    x_key: str
    y_keys: list[str]
    data: list[dict[str, Any]]
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    description: Optional[str] = None

class StructuredAnalysisResponse(BaseModel):
    answer: str
    key_findings: list[str] = []
    numerical_results: dict[str, Any] = {}
    execution_trace: list[ToolExecutionTraceItem] = []
    chart_config: Optional[ChartConfig] = None
    suggested_follow_ups: list[str] = []

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    role: str = "assistant"
    response: StructuredAnalysisResponse
    created_at: str

class SessionItem(BaseModel):
    id: str
    title: str
    dataset_id: Optional[str]
    dataset_name: Optional[str] = None
    created_at: str
    updated_at: str
    message_count: int = 0

class MessageHistoryItem(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    structured_data: Optional[StructuredAnalysisResponse] = None
    created_at: str

# Settings models
class SettingsUpdate(BaseModel):
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None

class SettingsStatus(BaseModel):
    api_key_configured: bool
    model: str
    max_tool_steps: int

# Report models
class ReportSummaryItem(BaseModel):
    id: str
    session_id: Optional[str]
    dataset_id: str
    title: str
    created_at: str
    pdf_available: bool

class ReportDetail(BaseModel):
    id: str
    session_id: Optional[str]
    dataset_id: str
    title: str
    content: dict[str, Any]
    created_at: str
    pdf_available: bool
