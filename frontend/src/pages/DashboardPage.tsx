import React, { useState } from 'react';
import { 
  Sparkles, 
  Database, 
  MessageSquare, 
  TrendingUp, 
  FileCheck2, 
  ArrowRight, 
  Upload,
  BarChart2,
  PieChart,
  ShieldAlert,
  Zap
} from 'lucide-react';
import { DatasetListItem, AnalysisSession } from '../types';

interface DashboardPageProps {
  datasets: DatasetListItem[];
  sessions: AnalysisSession[];
  onUploadClick: () => void;
  onSelectPrompt: (prompt: string) => void;
  onSelectSession: (id: string) => void;
  onNavigateToDatasets: () => void;
}

const CATEGORIZED_PROMPTS = {
  "Revenue & Performance": [
    "Which product generated the highest revenue?",
    "Calculate the average sales for each region and show a bar chart.",
    "Identify the top five performing categories by total revenue.",
    "Show monthly revenue trend for the leading product."
  ],
  "Categories & Segments": [
    "Compare revenue and average margin between different customer segments.",
    "Generate a pie chart showing market share by product category.",
    "Identify the lowest performing categories in terms of volume.",
    "Compare the top two categories across all regions."
  ],
  "Data Quality & Hygiene": [
    "Find all missing values and duplicate records across this dataset.",
    "Generate a complete data quality hygiene and health report.",
    "Check for any constant columns or zero-variance attributes.",
    "Calculate completeness percentage for every column."
  ],
  "Anomalies & Statistics": [
    "Detect statistical outliers in revenue and sales volume.",
    "Calculate the Pearson correlation between unit price and quantity.",
    "Identify unusual patterns and sales fluctuations across periods.",
    "Calculate standard deviation, median, and IQR for all numeric metrics."
  ]
};

export const DashboardPage: React.FC<DashboardPageProps> = ({
  datasets,
  sessions,
  onUploadClick,
  onSelectPrompt,
  onSelectSession,
  onNavigateToDatasets,
}) => {
  const [activeCategory, setActiveCategory] = useState<keyof typeof CATEGORIZED_PROMPTS>("Revenue & Performance");
  const totalRows = datasets.reduce((acc, d) => acc + d.row_count, 0);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white p-8 sm:p-10 border border-indigo-900/50 shadow-lg shadow-indigo-950/20">
        <div className="absolute right-0 top-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-medium mb-4 backdrop-blur-sm">
            <Sparkles className="w-3.5 h-3.5 text-indigo-300 animate-pulse" />
            <span>InsightOps AI Data Analyst Platform</span>
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-white mb-3">
            Your data. Your questions. Intelligent insights.
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed mb-6 font-normal">
            Interact with your CSV and Excel datasets using natural language. The autonomous agent orchestrates 27 validated Python functions to execute real computations without mathematical hallucinations.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => onSelectPrompt("What is the overall statistical summary of this dataset?")}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white font-medium text-xs transition shadow-sm shadow-indigo-500/30 cursor-pointer"
            >
              <Zap className="w-4 h-4" />
              <span>Ask First Question</span>
            </button>
            <button
              onClick={onUploadClick}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-white font-medium text-xs border border-white/20 transition cursor-pointer"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Dataset</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs flex items-center space-x-3.5">
          <div className="w-11 h-11 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Active Datasets</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-0.5">{datasets.length}</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs flex items-center space-x-3.5">
          <div className="w-11 h-11 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Records Analyzed</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-0.5">{totalRows.toLocaleString()}</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs flex items-center space-x-3.5">
          <div className="w-11 h-11 rounded-xl bg-purple-50 dark:bg-purple-950/60 flex items-center justify-center text-purple-600 dark:text-purple-400">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Analysis Sessions</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-0.5">{sessions.length}</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs flex items-center space-x-3.5">
          <div className="w-11 h-11 rounded-xl bg-amber-50 dark:bg-amber-950/60 flex items-center justify-center text-amber-600 dark:text-amber-400">
            <FileCheck2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Python Tool Engine</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-0.5">27 Verified Tools</p>
          </div>
        </div>
      </div>

      {/* Interactive Categorized Prompt Explorer */}
      <div className="p-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-500" />
              Interactive Analytics Questions
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Select a analytical domain to test the agent's tool execution workflow.
            </p>
          </div>

          {/* Category Tabs */}
          <div className="flex flex-wrap gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-slate-800">
            {Object.keys(CATEGORIZED_PROMPTS).map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat as any)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                  activeCategory === cat
                    ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Prompt Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
          {CATEGORIZED_PROMPTS[activeCategory].map((prompt, i) => (
            <button
              key={i}
              onClick={() => onSelectPrompt(prompt)}
              className="text-left p-3.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850/50 hover:bg-indigo-50/50 dark:hover:bg-indigo-950/30 hover:border-indigo-400 dark:hover:border-indigo-700/60 transition group text-xs text-slate-700 dark:text-slate-300 flex items-start justify-between cursor-pointer"
            >
              <span className="group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition leading-relaxed">
                "{prompt}"
              </span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-500 ml-3 mt-0.5 shrink-0 transition group-hover:translate-x-0.5" />
            </button>
          ))}
        </div>
      </div>

      {/* Available Datasets and Recent Sessions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Datasets in Library */}
        <div className="p-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Database className="w-4 h-4 text-indigo-500" />
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Loaded Datasets
              </h3>
            </div>
            <button
              onClick={onNavigateToDatasets}
              className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 font-medium cursor-pointer"
            >
              <span>Manage Library</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            {datasets.map((d) => (
              <div
                key={d.id}
                className="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-850/60 flex items-center justify-between"
              >
                <div>
                  <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                    {d.original_name}
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    {d.row_count.toLocaleString()} rows • {d.column_count} columns • {(d.file_size_bytes / 1024).toFixed(1)} KB
                  </p>
                </div>
                <button
                  onClick={() => onSelectPrompt(`Give me an overview of ${d.original_name}`)}
                  className="px-3 py-1.5 text-xs rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 font-medium transition cursor-pointer shadow-2xs"
                >
                  Analyze
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Analysis Sessions */}
        <div className="p-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs">
          <div className="flex items-center space-x-2 mb-4">
            <BarChart2 className="w-4 h-4 text-indigo-500" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Recent Analysis Sessions
            </h3>
          </div>

          {sessions.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-400 italic">
              No sessions started yet. Ask a question to begin!
            </div>
          ) : (
            <div className="space-y-2.5">
              {sessions.slice(0, 4).map((s) => (
                <div
                  key={s.id}
                  onClick={() => onSelectSession(s.id)}
                  className="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-850/60 hover:bg-slate-100/70 dark:hover:bg-slate-800 cursor-pointer flex items-center justify-between transition group"
                >
                  <div className="truncate pr-2">
                    <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition">
                      {s.title}
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      {s.dataset_name || 'Dataset'} • {s.message_count} messages
                    </p>
                  </div>
                  <span className="text-xs text-indigo-600 dark:text-indigo-400 font-medium shrink-0">
                    Resume →
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
