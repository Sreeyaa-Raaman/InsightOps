import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Sparkles, 
  Database, 
  Loader2, 
  Bot, 
  User, 
  FileDown, 
  CheckCircle2,
  HelpCircle,
  CornerDownLeft,
  RefreshCw,
  Copy,
  Check
} from 'lucide-react';
import { api } from '../services/api';
import { 
  ChatMessage, 
  DatasetListItem, 
} from '../types';
import { ChartRenderer } from '../components/ChartRenderer';
import { ExecutionTrace } from '../components/ExecutionTrace';

interface AnalystPageProps {
  selectedDatasetId: string;
  datasets: DatasetListItem[];
  currentSessionId: string | null;
  onSessionCreated: (id: string) => void;
  initialPrompt?: string;
  onClearInitialPrompt?: () => void;
  onNavigateToReports: (reportId: string) => void;
}

const DEFAULT_SUGGESTIONS = [
  "Which product generated the highest revenue?",
  "Calculate average sales for each region and show a bar chart.",
  "Identify top 5 performing categories.",
  "Detect outliers and fluctuations in sales.",
  "Compare revenue between different regions."
];

export const AnalystPage: React.FC<AnalystPageProps> = ({
  selectedDatasetId,
  datasets,
  currentSessionId,
  onSessionCreated,
  initialPrompt,
  onClearInitialPrompt,
  onNavigateToReports,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (currentSessionId) {
      loadHistory(currentSessionId);
    } else {
      setMessages([]);
    }
  }, [currentSessionId]);

  useEffect(() => {
    if (initialPrompt) {
      handleSend(initialPrompt);
      if (onClearInitialPrompt) onClearInitialPrompt();
    }
  }, [initialPrompt]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadHistory = async (sessionId: string) => {
    try {
      const history = await api.getSessionHistory(sessionId);
      setMessages(history);
    } catch (err) {
      console.error("Failed to load history", err);
    }
  };

  const handleSend = async (messageText: string) => {
    const text = messageText.trim();
    if (!text || !selectedDatasetId || loading) return;

    setErrorMsg(null);
    setInputMessage('');

    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: currentSessionId || 'new',
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const resp = await api.sendChatMessage(
        text,
        selectedDatasetId,
        currentSessionId || undefined
      );

      if (!currentSessionId) {
        onSessionCreated(resp.session_id);
      }

      const assistantMsg: ChatMessage = {
        id: resp.message_id,
        session_id: resp.session_id,
        role: 'assistant',
        content: resp.response.answer,
        structured_data: resp.response,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setErrorMsg(err.message || 'Agent failed to process query.');
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedDatasetId) return;
    setGeneratingReport(true);
    try {
      const report = await api.generateReport(
        selectedDatasetId,
        currentSessionId || undefined,
        `Executive Analysis Report - ${activeDataset?.original_name || 'Dataset'}`
      );
      onNavigateToReports(report.id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to generate report.');
    } finally {
      setGeneratingReport(false);
    }
  };

  const copyAnswer = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const activeDataset = datasets.find((d) => d.id === selectedDatasetId);

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)] bg-slate-50/70 dark:bg-slate-950 transition-colors">
      {/* Workspace Header Context Sub-bar */}
      <div className="px-6 py-2.5 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200/80 dark:border-slate-800 flex items-center justify-between text-xs sticky top-0 z-10">
        <div className="flex items-center space-x-2.5">
          <Database className="w-3.5 h-3.5 text-indigo-500" />
          <span className="text-slate-400 font-medium">Dataset Scope:</span>
          <span className="font-semibold text-slate-800 dark:text-slate-100">
            {activeDataset?.original_name || 'No Dataset Selected'}
          </span>
          {activeDataset && (
            <span className="hidden sm:inline-block text-[11px] text-slate-400 font-mono">
              • {activeDataset.row_count.toLocaleString()} rows
            </span>
          )}
        </div>

        <button
          onClick={handleGenerateReport}
          disabled={generatingReport || !selectedDatasetId}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition disabled:opacity-50 cursor-pointer shadow-2xs"
        >
          {generatingReport ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <FileDown className="w-3.5 h-3.5 text-indigo-500" />
          )}
          <span>Generate Formal PDF Report</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl w-full mx-auto">
        {messages.length === 0 ? (
          <div className="py-16 text-center max-w-lg mx-auto space-y-5 animate-in fade-in duration-300">
            <div className="w-14 h-14 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200/80 dark:border-indigo-800/80 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mx-auto shadow-xs">
              <Sparkles className="w-7 h-7" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                InsightOps AI Analyst Ready
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-1.5">
                Ask questions about revenue, distributions, top performers, or anomalies. The agent inspects columns, executes deterministic Python operations, and visualizes verified answers.
              </p>
            </div>

            <div className="pt-2 text-left space-y-2">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block px-1">
                Suggested Prompts
              </span>
              <div className="space-y-1.5">
                {DEFAULT_SUGGESTIONS.map((sug, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(sug)}
                    className="w-full text-left p-3 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-indigo-500 dark:hover:border-indigo-600 text-xs text-slate-700 dark:text-slate-300 transition cursor-pointer shadow-2xs flex items-center justify-between group"
                  >
                    <span>"{sug}"</span>
                    <CornerDownLeft className="w-3 h-3 text-slate-400 opacity-0 group-hover:opacity-100 transition" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 text-xs animate-in fade-in duration-200 ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-xs shadow-indigo-500/20">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl p-4.5 shadow-xs transition-all ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-xs shadow-indigo-600/10'
                    : 'bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-xs'
                }`}
              >
                {/* Explainable Tool Execution Stepper */}
                {msg.role === 'assistant' && msg.structured_data?.execution_trace && (
                  <ExecutionTrace trace={msg.structured_data.execution_trace} />
                )}

                {/* Primary Answer Text */}
                <div className="prose dark:prose-invert text-xs leading-relaxed whitespace-pre-line font-sans">
                  {msg.content}
                </div>

                {/* Structured Key Findings */}
                {msg.role === 'assistant' &&
                  msg.structured_data?.key_findings &&
                  msg.structured_data.key_findings.length > 0 && (
                    <div className="mt-3.5 pt-3 border-t border-slate-100 dark:border-slate-800/80 space-y-1.5">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
                        Verified Analytical Takeaways
                      </span>
                      {msg.structured_data.key_findings.map((finding, idx) => (
                        <div key={idx} className="flex items-start space-x-2 text-[11px] text-slate-700 dark:text-slate-300">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                          <span className="leading-snug">{finding}</span>
                        </div>
                      ))}
                    </div>
                  )}

                {/* Dynamic Chart Renderer */}
                {msg.role === 'assistant' && msg.structured_data?.chart_config && (
                  <ChartRenderer config={msg.structured_data.chart_config} />
                )}

                {/* Numerical Results Badges */}
                {msg.role === 'assistant' &&
                  msg.structured_data?.numerical_results &&
                  Object.keys(msg.structured_data.numerical_results).length > 0 && (
                    <div className="mt-3.5 flex flex-wrap gap-1.5">
                      {Object.entries(msg.structured_data.numerical_results).map(([k, v]) => {
                        if (typeof v === 'object') return null;
                        return (
                          <div
                            key={k}
                            className="text-[10px] font-mono px-2.5 py-1 rounded-lg bg-slate-100/90 dark:bg-slate-800/90 text-slate-700 dark:text-slate-300 border border-slate-200/70 dark:border-slate-700"
                          >
                            <span className="text-slate-400">{k}:</span>{' '}
                            <span className="font-semibold text-indigo-600 dark:text-indigo-400">
                              {typeof v === 'number' ? v.toLocaleString() : String(v)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  )}

                {/* Copy Answer Button */}
                {msg.role === 'assistant' && (
                  <div className="mt-2.5 pt-2 flex items-center justify-end">
                    <button
                      onClick={() => copyAnswer(msg.content, index)}
                      className="flex items-center space-x-1 text-[10px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition cursor-pointer"
                    >
                      {copiedIndex === index ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-500" />
                          <span className="text-emerald-500 font-medium">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy Answer</span>
                        </>
                      )}
                    </button>
                  </div>
                )}

                {/* Suggested Follow-up chips */}
                {msg.role === 'assistant' &&
                  msg.structured_data?.suggested_follow_ups &&
                  msg.structured_data.suggested_follow_ups.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800/80">
                      <span className="text-[10px] text-slate-400 block mb-1.5 flex items-center gap-1 font-medium">
                        <HelpCircle className="w-3 h-3 text-indigo-400" />
                        Suggested Follow-up Inquiries
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.structured_data.suggested_follow_ups.map((sug, i) => (
                          <button
                            key={i}
                            onClick={() => handleSend(sug)}
                            className="text-[11px] px-3 py-1 rounded-full bg-indigo-50/80 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900 border border-indigo-200/60 dark:border-indigo-800/50 transition cursor-pointer text-left"
                          >
                            + {sug}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-slate-700 dark:text-slate-300 shrink-0 mt-0.5 shadow-2xs">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex items-start space-x-3 text-xs animate-in fade-in duration-150">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-0.5 animate-pulse shadow-xs shadow-indigo-500/20">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl rounded-tl-xs p-4 shadow-xs flex items-center space-x-3 text-slate-600 dark:text-slate-300">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
              <span>Analyzing schema & orchestrating verified Python operations...</span>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300 text-xs">
            {errorMsg}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200/80 dark:border-slate-800 transition-colors">
        <div className="max-w-4xl mx-auto">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(inputMessage);
            }}
            className="relative flex items-center"
          >
            <input
              ref={inputRef}
              type="text"
              placeholder="Ask anything about your data (e.g. 'Which product generated the highest revenue?')"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={loading || !selectedDatasetId}
              className="w-full text-xs pl-4 pr-12 py-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 shadow-xs disabled:opacity-50 transition"
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim() || !selectedDatasetId}
              className="absolute right-2.5 p-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-30 transition shadow-xs cursor-pointer active:scale-95"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 px-1 font-sans">
            <span>Orchestrates 27 validated Python tools via Google Gemini Function Calling</span>
            <span className="hidden sm:inline font-mono text-[10px]">Press Enter to send ↵</span>
          </div>
        </div>
      </div>
    </div>
  );
};
