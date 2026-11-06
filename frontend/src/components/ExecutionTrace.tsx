import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Terminal, CheckCircle2, AlertCircle, Play } from 'lucide-react';
import { ToolExecutionTraceItem } from '../types';

interface ExecutionTraceProps {
  trace: ToolExecutionTraceItem[];
}

export const ExecutionTrace: React.FC<ExecutionTraceProps> = ({ trace }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!trace || trace.length === 0) return null;

  return (
    <div className="mb-3.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/60 overflow-hidden text-xs transition">
      {/* Header Toggle Bar */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3.5 py-2.5 text-left font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100/70 dark:hover:bg-slate-800/50 transition cursor-pointer"
      >
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
            <Terminal className="w-3 h-3" />
          </div>
          <span className="font-semibold text-[11px] tracking-tight text-slate-700 dark:text-slate-200">
            Agent Reasoning & Python Execution
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-100/70 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 font-semibold">
            {trace.length} tool {trace.length === 1 ? 'call' : 'calls'}
          </span>
        </div>
        <div className="flex items-center space-x-1 text-slate-400 text-[11px]">
          <span>{isOpen ? 'Collapse' : 'Inspect'}</span>
          {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        </div>
      </button>

      {/* Expanded Timeline Steps */}
      {isOpen && (
        <div className="px-4 py-3 border-t border-slate-200/70 dark:border-slate-800 space-y-3 bg-white/40 dark:bg-slate-950/40">
          {trace.map((item, idx) => {
            const isSuccess = item.status === 'success';
            return (
              <div key={idx} className="relative flex items-start space-x-3 text-xs">
                {/* Step indicator circle */}
                <div className="flex flex-col items-center">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    isSuccess
                      ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800'
                      : 'bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400 border border-amber-300 dark:border-amber-800'
                  }`}>
                    {idx + 1}
                  </div>
                  {idx < trace.length - 1 && (
                    <div className="w-0.5 h-full bg-slate-200 dark:bg-slate-800 my-1"></div>
                  )}
                </div>

                {/* Step detail card */}
                <div className="flex-1 pb-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-semibold text-indigo-600 dark:text-indigo-400 text-[11px]">
                      {item.tool_name}()
                    </span>
                    <span className="text-[10px] text-slate-400">
                      • {item.description}
                    </span>
                  </div>
                  <p className="text-slate-700 dark:text-slate-300 text-[11px] mt-0.5 font-sans leading-relaxed">
                    {item.summary}
                  </p>
                  {item.parameters && Object.keys(item.parameters).length > 0 && (
                    <div className="mt-1 font-mono text-[10px] text-slate-500 dark:text-slate-400 bg-slate-100/90 dark:bg-slate-900 px-2 py-0.5 rounded border border-slate-200/50 dark:border-slate-800 inline-block">
                      params: {JSON.stringify(item.parameters)}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
