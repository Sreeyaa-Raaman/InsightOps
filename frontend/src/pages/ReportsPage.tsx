import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  FileSpreadsheet, 
  Loader2, 
  ShieldCheck, 
  AlertTriangle,
  FileDown,
  Calendar,
  Layers,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { ReportItem, ReportDetail, DatasetListItem } from '../types';

interface ReportsPageProps {
  datasets: DatasetListItem[];
  selectedDatasetId: string;
  initialReportId?: string;
  onClearInitialReportId?: () => void;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({
  datasets,
  selectedDatasetId,
  initialReportId,
  onClearInitialReportId,
}) => {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [activeReport, setActiveReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadReports();
  }, []);

  useEffect(() => {
    if (initialReportId) {
      loadReportDetail(initialReportId);
      if (onClearInitialReportId) onClearInitialReportId();
    }
  }, [initialReportId]);

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await api.listReports();
      setReports(data);
      if (data.length > 0 && !activeReport) {
        loadReportDetail(data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadReportDetail = async (id: string) => {
    try {
      const detail = await api.getReport(id);
      setActiveReport(detail);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async () => {
    if (!selectedDatasetId) return;
    setGenerating(true);
    try {
      const ds = datasets.find((d) => d.id === selectedDatasetId);
      const rep = await api.generateReport(
        selectedDatasetId,
        undefined,
        `Executive Analysis Report - ${ds?.original_name || 'Dataset'}`
      );
      await loadReports();
      setActiveReport(rep);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            Executive Reports & Quantitative Exports
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Generate and download publication-ready executive PDF summaries and CSV metric tables computed from your datasets.
          </p>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating || !selectedDatasetId}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium transition shadow-xs shadow-indigo-500/20 disabled:opacity-50 cursor-pointer"
        >
          {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileDown className="w-4 h-4" />}
          <span>Generate Executive Report</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports Navigation Sidebar */}
        <div className="p-4.5 rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-2.5 h-fit">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block px-2 mb-1">
            Generated Documents ({reports.length})
          </span>

          {loading ? (
            <div className="py-8 text-center text-xs text-slate-400">Loading reports...</div>
          ) : reports.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-400 italic">
              No reports generated yet. Click "Generate Executive Report" to create one.
            </div>
          ) : (
            reports.map((r) => {
              const isSelected = activeReport?.id === r.id;
              return (
                <div
                  key={r.id}
                  onClick={() => loadReportDetail(r.id)}
                  className={`p-3.5 rounded-xl border transition cursor-pointer text-xs ${
                    isSelected
                      ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/40 text-indigo-900 dark:text-indigo-200 shadow-xs'
                      : 'border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850 hover:border-slate-300 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  <h4 className="font-semibold truncate">{r.title}</h4>
                  <div className="mt-1.5 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                    <span className="flex items-center gap-1 font-sans">
                      <Calendar className="w-3 h-3 text-slate-400" />
                      {r.created_at.split(' ')[0]}
                    </span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
                      PDF Ready
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Detailed Report View */}
        <div className="lg:col-span-2">
          {activeReport ? (
            <div className="p-7 rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-6">
              {/* Header and Download Action Buttons */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-5 border-b border-slate-200/80 dark:border-slate-800 gap-3">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    {activeReport.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Dataset: <span className="font-medium text-slate-700 dark:text-slate-300">{activeReport.content.dataset_name}</span> • Generated {activeReport.content.generated_at}
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <a
                    href={api.getReportPdfUrl(activeReport.id)}
                    download
                    className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium transition shadow-xs shadow-indigo-500/20 cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF</span>
                  </a>
                  <a
                    href={api.getReportCsvUrl(activeReport.id)}
                    download
                    className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-medium transition cursor-pointer"
                  >
                    <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Export CSV</span>
                  </a>
                </div>
              </div>

              {/* Data Health Score Card */}
              <div className="p-4.5 rounded-xl bg-slate-50/90 dark:bg-slate-850/90 border border-slate-200/80 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center space-x-3.5">
                  <div className="w-11 h-11 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                      Data Hygiene & Quality Score
                    </h4>
                    <p className="text-[11px] text-slate-500">
                      Evaluated for null ratios, row duplication, and zero-variance columns
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                    {activeReport.content.health_score}/100
                  </span>
                  <span className="block text-[10px] font-semibold uppercase text-slate-400">
                    Grade {activeReport.content.health_grade}
                  </span>
                </div>
              </div>

              {/* Dataset Dimensions */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5" />
                  Dataset Attributes & Dimensions
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Total Records</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">
                      {activeReport.content.dimensions?.rows?.toLocaleString()}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Attributes</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">
                      {activeReport.content.dimensions?.columns}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Quality Issues</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">
                      {activeReport.content.data_quality_issues?.length || 0}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Engine</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">
                      Python / Pandas
                    </span>
                  </div>
                </div>
              </div>

              {/* Numeric Metrics Summary Table */}
              {activeReport.content.numeric_metrics && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5">
                    Calculated Numeric Metrics Summary
                  </h4>
                  <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-50 dark:bg-slate-850 text-slate-500 text-[10px] border-b border-slate-200 dark:border-slate-800">
                        <tr>
                          <th className="py-2.5 px-3">Column</th>
                          <th className="py-2.5 px-3">Mean</th>
                          <th className="py-2.5 px-3">Median</th>
                          <th className="py-2.5 px-3">Min</th>
                          <th className="py-2.5 px-3">Max</th>
                          <th className="py-2.5 px-3">Total Sum</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-[11px]">
                        {Object.entries(activeReport.content.numeric_metrics).map(([col, stats]: any) => (
                          <tr key={col}>
                            <td className="py-2.5 px-3 font-semibold text-slate-800 dark:text-slate-200 font-sans">
                              {col}
                            </td>
                            <td className="py-2.5 px-3 text-slate-600 dark:text-slate-300">{stats.mean?.toLocaleString()}</td>
                            <td className="py-2.5 px-3 text-slate-600 dark:text-slate-300">{stats.median?.toLocaleString()}</td>
                            <td className="py-2.5 px-3 text-slate-600 dark:text-slate-300">{stats.min?.toLocaleString()}</td>
                            <td className="py-2.5 px-3 text-slate-600 dark:text-slate-300">{stats.max?.toLocaleString()}</td>
                            <td className="py-2.5 px-3 font-bold text-indigo-600 dark:text-indigo-400">{stats.total?.toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Data Quality Issues */}
              {activeReport.content.data_quality_issues?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                    Data Quality Observations & Recommendations
                  </h4>
                  <div className="space-y-2">
                    {activeReport.content.data_quality_issues.map((issue: any, i: number) => (
                      <div
                        key={i}
                        className="p-3.5 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-800/40 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-amber-900 dark:text-amber-200">
                            {issue.column}: {issue.type}
                          </span>
                          <span className="text-[10px] px-2 py-0.5 rounded-md bg-amber-200/60 dark:bg-amber-900 text-amber-800 dark:text-amber-200 font-medium">
                            {issue.severity} Severity
                          </span>
                        </div>
                        <p className="text-[11px] text-amber-800 dark:text-amber-300 mt-1">
                          {issue.recommendation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strategic Recommendations */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5">
                  Strategic Recommendations
                </h4>
                <div className="space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
                  {activeReport.content.recommendations?.map((rec: string, i: number) => (
                    <div key={i} className="flex items-start space-x-2">
                      <span className="text-indigo-600 font-bold">•</span>
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="py-24 text-center text-xs text-slate-400 border border-slate-200 dark:border-slate-800 rounded-2xl bg-white dark:bg-slate-900">
              Select or generate an executive report to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
