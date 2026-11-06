import React, { useState } from 'react';
import { X, ShieldCheck, Cpu, Sliders, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentModel: string;
  isConfigured: boolean;
  onSaved: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  currentModel,
  onSaved,
}) => {
  const [model, setModel] = useState(currentModel || 'gemini-2.5-flash');
  const [maxSteps, setMaxSteps] = useState(8);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  if (!isOpen) return null;

  const handleSave = async () => {
    setSaving(true);
    setTestResult(null);
    try {
      await api.updateSettings({
        gemini_model: model,
        max_tool_steps: maxSteps,
      });
      onSaved();
      setTestResult({ success: true, message: 'Settings applied successfully.' });
    } catch (err: any) {
      setTestResult({ success: false, message: err.message || 'Failed to update settings' });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      if (model !== currentModel) {
        await api.updateSettings({ gemini_model: model, max_tool_steps: maxSteps });
      }
      const res = await api.testGemini();
      setTestResult(res);
      if (res.success) onSaved();
    } catch (err: any) {
      setTestResult({ success: false, message: err.message || 'Connection test failed' });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              System Settings & Agent Preferences
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4 text-xs">
          {/* Active System Key Status Banner */}
          <div className="p-3.5 rounded-xl bg-emerald-50/80 dark:bg-emerald-950/40 border border-emerald-200/80 dark:border-emerald-800/60 flex items-start space-x-3">
            <ShieldCheck className="w-4 h-4 mt-0.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <div>
              <p className="font-semibold text-emerald-900 dark:text-emerald-200">
                System API Key: Active & Encrypted
              </p>
              <p className="text-[11px] text-emerald-800/90 dark:text-emerald-300/80 mt-0.5 leading-relaxed">
                The central Google Gemini API key is configured and managed at the server level. Users are not required to input or manage credentials.
              </p>
            </div>
          </div>

          {/* Model Architecture Selector */}
          <div>
            <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Gemini LLM Architecture
            </label>
            <div className="relative">
              <Cpu className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full text-xs pl-8 pr-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
              >
                <option value="gemini-3.1-flash-lite">Gemini 3.1 Flash Lite (Recommended - High Speed & Tool Calling)</option>
                <option value="gemini-3.8-flash">Gemini 3.8 Flash (High Performance)</option>
                <option value="gemini-2.5-pro">Gemini 2.5 Pro (Deep Multistep Reasoning)</option>
              </select>
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              Select the Gemini foundation model used for tool orchestration.
            </p>
          </div>

          {/* Max Tool Execution Steps */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="font-medium text-slate-700 dark:text-slate-300">
                Max Tool Execution Depth
              </label>
              <span className="font-mono text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                {maxSteps} steps
              </span>
            </div>
            <input
              type="range"
              min={3}
              max={15}
              value={maxSteps}
              onChange={(e) => setMaxSteps(Number(e.target.value))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
              <span>Fast (3 steps)</span>
              <span>Balanced (8 steps)</span>
              <span>Deep (15 steps)</span>
            </div>
          </div>

          {/* Test Status Feedback */}
          {testResult && (
            <div
              className={`p-2.5 rounded-xl text-[11px] font-mono flex items-start space-x-2 ${
                testResult.success
                  ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                  : 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800'
              }`}
            >
              {testResult.success ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
              )}
              <span className="leading-snug">{testResult.message}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850/50 flex items-center justify-end space-x-2">
          <button
            onClick={handleTest}
            disabled={testing || saving}
            className="px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium transition disabled:opacity-50 flex items-center space-x-1.5 text-xs cursor-pointer"
          >
            {testing && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            <span>Test Model Connectivity</span>
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium transition disabled:opacity-50 text-xs shadow-xs shadow-indigo-500/20 flex items-center space-x-1.5 cursor-pointer"
          >
            {saving && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            <span>Save Preferences</span>
          </button>
        </div>
      </div>
    </div>
  );
};
