import React from 'react';
import { Database, ChevronDown, Activity, Sparkles, Plus } from 'lucide-react';
import { DatasetListItem } from '../types';

interface NavbarProps {
  datasets: DatasetListItem[];
  selectedDatasetId: string;
  onSelectDataset: (id: string) => void;
  onUploadClick: () => void;
  apiConfigured?: boolean;
  modelName?: string;
  onOpenSettings?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  datasets,
  selectedDatasetId,
  onSelectDataset,
  onUploadClick,
}) => {
  const currentDataset = datasets.find((d) => d.id === selectedDatasetId);

  return (
    <header className="h-14 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/75 dark:bg-slate-900/75 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20 transition-colors">
      {/* Left: Breadcrumbs & Active Dataset Dropdown */}
      <div className="flex items-center space-x-3">
        <div className="hidden sm:flex items-center space-x-2 text-xs font-medium text-slate-400 dark:text-slate-500">
          <span>InsightOps</span>
          <span>/</span>
        </div>

        {/* Custom Dataset Selector Pill */}
        <div className="relative group">
          <div className="flex items-center space-x-2 bg-slate-100/90 dark:bg-slate-800/90 hover:bg-slate-200/80 dark:hover:bg-slate-700/80 border border-slate-200 dark:border-slate-700/70 rounded-lg px-3 py-1.5 transition cursor-pointer shadow-xs">
            <Database className="w-3.5 h-3.5 text-indigo-500" />
            <select
              value={selectedDatasetId}
              onChange={(e) => onSelectDataset(e.target.value)}
              className="appearance-none bg-transparent text-xs font-medium text-slate-800 dark:text-slate-100 pr-5 focus:outline-none cursor-pointer"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id} className="dark:bg-slate-900 text-slate-800 dark:text-slate-100">
                  {d.original_name} ({d.row_count.toLocaleString()} rows)
                </option>
              ))}
            </select>
            <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 pointer-events-none" />
          </div>
        </div>

        {currentDataset && (
          <span className="hidden md:inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 border border-indigo-200/50 dark:border-indigo-800/40">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
            {currentDataset.column_count} columns loaded
          </span>
        )}
      </div>

      {/* Right: Engine Status Badge & Actions */}
      <div className="flex items-center space-x-3">
        {/* Subtle, Confidential Engine Status Indicator (No loud API Key badge) */}
        <div className="flex items-center space-x-2 px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-100/70 dark:bg-slate-800/60 text-slate-600 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700/50">
          <Activity className="w-3.5 h-3.5 text-emerald-500" />
          <span className="hidden sm:inline">Python Analytics Engine:</span>
          <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Active</span>
        </div>

        {/* Upload Button */}
        <button
          onClick={onUploadClick}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium transition shadow-xs shadow-indigo-500/20"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Upload Dataset</span>
        </button>
      </div>
    </header>
  );
};
