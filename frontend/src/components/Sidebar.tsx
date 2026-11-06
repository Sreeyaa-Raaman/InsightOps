import React, { useState } from 'react';
import { 
  BarChart3, 
  MessageSquare, 
  Database, 
  FileText, 
  Plus, 
  Settings, 
  Trash2, 
  Sparkles,
  Sun,
  Moon,
  Search
} from 'lucide-react';
import { AnalysisSession } from '../types';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  sessions: AnalysisSession[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewAnalysis: () => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  onOpenSettings: () => void;
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  sessions,
  currentSessionId,
  onSelectSession,
  onNewAnalysis,
  onDeleteSession,
  onOpenSettings,
  darkMode,
  setDarkMode,
}) => {
  const [sessionSearch, setSessionSearch] = useState('');

  const filteredSessions = sessions.filter((s) =>
    (s.title || '').toLowerCase().includes(sessionSearch.toLowerCase()) ||
    (s.dataset_name || '').toLowerCase().includes(sessionSearch.toLowerCase())
  );

  return (
    <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200/80 dark:border-slate-800/80 flex flex-col h-screen select-none transition-colors">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-200/70 dark:border-slate-800/70 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center text-white shadow-sm shadow-indigo-500/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h1 className="font-semibold text-sm tracking-tight text-slate-900 dark:text-white flex items-center gap-1.5">
              InsightOps
              <span className="text-[9px] font-mono font-medium px-1.5 py-0.2 rounded bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 border border-indigo-200/60 dark:border-indigo-800/50">
                PRO
              </span>
            </h1>
            <p className="text-[10px] text-slate-400 font-mono tracking-tight">AI Data Analyst Agent</p>
          </div>
        </div>
      </div>

      {/* New Analysis Action Button */}
      <div className="p-3">
        <button
          onClick={onNewAnalysis}
          className="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium transition shadow-xs shadow-indigo-500/25 active:scale-[0.99] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>New Analysis</span>
        </button>
      </div>

      {/* Primary Navigation */}
      <div className="px-3 py-1 space-y-1">
        <button
          onClick={() => setCurrentTab('dashboard')}
          className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition cursor-pointer ${
            currentTab === 'dashboard'
              ? 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 font-semibold'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Dashboard</span>
        </button>

        <button
          onClick={() => setCurrentTab('analyst')}
          className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition cursor-pointer ${
            currentTab === 'analyst'
              ? 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 font-semibold'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>AI Analyst Workspace</span>
        </button>

        <button
          onClick={() => setCurrentTab('datasets')}
          className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition cursor-pointer ${
            currentTab === 'datasets'
              ? 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 font-semibold'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60'
          }`}
        >
          <Database className="w-4 h-4" />
          <span>Dataset Library</span>
        </button>

        <button
          onClick={() => setCurrentTab('reports')}
          className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition cursor-pointer ${
            currentTab === 'reports'
              ? 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 font-semibold'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Executive Reports</span>
        </button>
      </div>

      {/* Recent Sessions List with Search */}
      <div className="flex-1 flex flex-col min-h-0 px-3 py-2 mt-2 border-t border-slate-100 dark:border-slate-800/70">
        <div className="flex items-center justify-between px-2 mb-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Recent Sessions
          </span>
          {sessions.length > 0 && (
            <span className="text-[10px] font-mono text-slate-400">
              {sessions.length}
            </span>
          )}
        </div>

        {sessions.length > 4 && (
          <div className="relative mb-2 px-1">
            <Search className="w-3 h-3 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter sessions..."
              value={sessionSearch}
              onChange={(e) => setSessionSearch(e.target.value)}
              className="w-full text-[11px] pl-6 pr-2 py-1 rounded-lg bg-slate-100/70 dark:bg-slate-800/60 border border-slate-200/50 dark:border-slate-700/50 text-slate-700 dark:text-slate-200 focus:outline-none"
            />
          </div>
        )}

        <div className="flex-1 overflow-y-auto space-y-0.5">
          {filteredSessions.length === 0 ? (
            <div className="text-[11px] text-slate-400 px-3 py-3 italic">
              {sessionSearch ? 'No matching sessions' : 'No previous sessions'}
            </div>
          ) : (
            filteredSessions.map((s) => (
              <div
                key={s.id}
                onClick={() => {
                  onSelectSession(s.id);
                  setCurrentTab('analyst');
                }}
                className={`group flex items-center justify-between px-2.5 py-2 rounded-lg text-xs cursor-pointer transition ${
                  currentSessionId === s.id && currentTab === 'analyst'
                    ? 'bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100/70 dark:hover:bg-slate-800/60'
                }`}
              >
                <div className="truncate flex-1 pr-1.5">
                  <p className="truncate text-xs">{s.title || 'Analysis Session'}</p>
                  {s.dataset_name && (
                    <span className="text-[10px] text-slate-400 block truncate">
                      {s.dataset_name}
                    </span>
                  )}
                </div>
                <button
                  onClick={(e) => onDeleteSession(s.id, e)}
                  title="Delete Session"
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 rounded transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer Settings & Theme Toggle */}
      <div className="p-3 border-t border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between text-xs">
        <button
          onClick={onOpenSettings}
          className="flex items-center space-x-1.5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white px-2 py-1.5 rounded-lg transition hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <Settings className="w-4 h-4" />
          <span>System Settings</span>
        </button>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-1.5 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
};
