export interface ColumnInfo {
  name: string;
  dtype: string;
  non_null_count: number;
  null_count: number;
  unique_count: number;
  sample_values: any[];
}

export interface DatasetListItem {
  id: string;
  original_name: string;
  row_count: number;
  column_count: number;
  file_size_bytes: number;
  created_at: string;
}

export interface DatasetOverview {
  id: string;
  filename: string;
  original_name: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  columns: ColumnInfo[];
  created_at: string;
}

export interface DatasetPreview {
  id: string;
  original_name: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  dtypes: Record<string, string>;
  rows: Record<string, any>[];
}

export interface ToolExecutionTraceItem {
  tool_name: string;
  description: string;
  parameters: Record<string, any>;
  status: string;
  summary: string;
}

export interface ChartConfig {
  chart_type: 'bar' | 'line' | 'pie' | 'histogram' | 'scatter';
  title: string;
  x_key: string;
  y_keys: string[];
  data: Record<string, any>[];
  x_label?: string;
  y_label?: string;
  description?: string;
}

export interface StructuredAnalysisResponse {
  answer: string;
  key_findings: string[];
  numerical_results: Record<string, any>;
  execution_trace: ToolExecutionTraceItem[];
  chart_config?: ChartConfig | null;
  suggested_follow_ups: string[];
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  structured_data?: StructuredAnalysisResponse | null;
  created_at: string;
}

export interface AnalysisSession {
  id: string;
  title: string;
  dataset_id?: string | null;
  dataset_name?: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ReportItem {
  id: string;
  session_id?: string | null;
  dataset_id: string;
  title: string;
  created_at: string;
  pdf_available: boolean;
}

export interface ReportDetail extends ReportItem {
  content: Record<string, any>;
}

export interface SettingsStatus {
  api_key_configured: boolean;
  model: string;
  max_tool_steps: number;
}
