import {
  DatasetListItem,
  DatasetOverview,
  DatasetPreview,
  ChatMessage,
  AnalysisSession,
  StructuredAnalysisResponse,
  ReportItem,
  ReportDetail,
  SettingsStatus
} from '../types';

const API_BASE = '/api';

export const api = {
  // Health & Settings
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return res.json();
  },

  async getSettings(): Promise<SettingsStatus> {
    const res = await fetch(`${API_BASE}/settings`);
    if (!res.ok) throw new Error('Failed to fetch settings');
    return res.json();
  },

  async updateSettings(data: { gemini_model?: string; max_tool_steps?: number }): Promise<SettingsStatus> {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  async testGemini(): Promise<{ success: boolean; message: string; model?: string }> {
    const res = await fetch(`${API_BASE}/settings/test`, { method: 'POST' });
    return res.json();
  },

  // Datasets
  async listDatasets(): Promise<DatasetListItem[]> {
    const res = await fetch(`${API_BASE}/datasets`);
    if (!res.ok) throw new Error('Failed to fetch datasets');
    return res.json();
  },

  async getDatasetOverview(id: string): Promise<DatasetOverview> {
    const res = await fetch(`${API_BASE}/datasets/${id}`);
    if (!res.ok) throw new Error('Failed to fetch dataset');
    return res.json();
  },

  async getDatasetPreview(id: string, limit = 15): Promise<DatasetPreview> {
    const res = await fetch(`${API_BASE}/datasets/${id}/preview?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to load dataset preview');
    return res.json();
  },

  async uploadDataset(file: File): Promise<DatasetOverview> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/datasets/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  // Agent Chat & Sessions
  async listSessions(): Promise<AnalysisSession[]> {
    const res = await fetch(`${API_BASE}/agent/sessions`);
    if (!res.ok) throw new Error('Failed to fetch sessions');
    return res.json();
  },

  async createSession(dataset_id?: string, title?: string): Promise<AnalysisSession> {
    const res = await fetch(`${API_BASE}/agent/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset_id, title }),
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  async getSessionHistory(sessionId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${API_BASE}/agent/history/${sessionId}`);
    if (!res.ok) throw new Error('Failed to fetch chat history');
    return res.json();
  },

  async deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/agent/history/${sessionId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete session');
  },

  async sendChatMessage(
    message: string,
    dataset_id: string,
    session_id?: string
  ): Promise<{ session_id: string; message_id: string; response: StructuredAnalysisResponse }> {
    const res = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, dataset_id, session_id }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(err.detail || 'Analysis failed');
    }
    return res.json();
  },

  // Reports
  async listReports(): Promise<ReportItem[]> {
    const res = await fetch(`${API_BASE}/reports`);
    if (!res.ok) throw new Error('Failed to fetch reports');
    return res.json();
  },

  async generateReport(dataset_id: string, session_id?: string, title?: string): Promise<ReportDetail> {
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset_id, session_id, title }),
    });
    if (!res.ok) throw new Error('Failed to generate report');
    return res.json();
  },

  async getReport(reportId: string): Promise<ReportDetail> {
    const res = await fetch(`${API_BASE}/reports/${reportId}`);
    if (!res.ok) throw new Error('Failed to load report');
    return res.json();
  },

  getReportPdfUrl(reportId: string): string {
    return `${API_BASE}/reports/${reportId}/download`;
  },

  getReportCsvUrl(reportId: string): string {
    return `${API_BASE}/reports/${reportId}/download-csv`;
  }
};
