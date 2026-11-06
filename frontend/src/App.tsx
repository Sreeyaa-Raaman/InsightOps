import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { SettingsModal } from './components/SettingsModal';
import { DashboardPage } from './pages/DashboardPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { AnalystPage } from './pages/AnalystPage';
import { ReportsPage } from './pages/ReportsPage';
import { api } from './services/api';
import { DatasetListItem, AnalysisSession, SettingsStatus } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [datasets, setDatasets] = useState<DatasetListItem[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
  const [sessions, setSessions] = useState<AnalysisSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  // Prompt forwarding from Dashboard to Analyst
  const [initialPrompt, setInitialPrompt] = useState<string | undefined>(undefined);
  const [initialReportId, setInitialReportId] = useState<string | undefined>(undefined);

  // Settings & Theme
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [settingsStatus, setSettingsStatus] = useState<SettingsStatus>({
    api_key_configured: false,
    model: 'gemini-3.1-flash-lite',
    max_tool_steps: 8,
  });

  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [dsList, sessList, settingsData] = await Promise.all([
        api.listDatasets(),
        api.listSessions(),
        api.getSettings(),
      ]);
      setDatasets(dsList);
      if (dsList.length > 0 && !selectedDatasetId) {
        setSelectedDatasetId(dsList[0].id);
      }
      setSessions(sessList);
      setSettingsStatus(settingsData);
    } catch (err) {
      console.error('Failed to load initial workspace data', err);
    }
  };

  const handleRefreshDatasets = async () => {
    try {
      const dsList = await api.listDatasets();
      setDatasets(dsList);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRefreshSessions = async () => {
    try {
      const sessList = await api.listSessions();
      setSessions(sessList);
    } catch (err) {
      console.error(err);
    }
  };

  const handleNewAnalysis = () => {
    setCurrentSessionId(null);
    setCurrentTab('analyst');
  };

  const handleDeleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteSession(id);
      if (currentSessionId === id) {
        setCurrentSessionId(null);
      }
      await handleRefreshSessions();
    } catch (err) {
      console.error('Failed to delete session', err);
    }
  };

  const handleSelectPromptFromDashboard = (prompt: string) => {
    setInitialPrompt(prompt);
    setCurrentTab('analyst');
  };

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden font-sans">
      {/* Left Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={(id) => {
          setCurrentSessionId(id);
          const sess = sessions.find((s) => s.id === id);
          if (sess?.dataset_id) {
            setSelectedDatasetId(sess.dataset_id);
          }
        }}
        onNewAnalysis={handleNewAnalysis}
        onDeleteSession={handleDeleteSession}
        onOpenSettings={() => setIsSettingsOpen(true)}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Navbar */}
        <Navbar
          datasets={datasets}
          selectedDatasetId={selectedDatasetId}
          onSelectDataset={setSelectedDatasetId}
          onUploadClick={() => setCurrentTab('datasets')}
          apiConfigured={settingsStatus.api_key_configured}
          modelName={settingsStatus.model}
          onOpenSettings={() => setIsSettingsOpen(true)}
        />

        {/* Tab View Container */}
        <main className="flex-1 overflow-y-auto">
          {currentTab === 'dashboard' && (
            <DashboardPage
              datasets={datasets}
              sessions={sessions}
              onUploadClick={() => setCurrentTab('datasets')}
              onSelectPrompt={handleSelectPromptFromDashboard}
              onSelectSession={(id) => {
                setCurrentSessionId(id);
                setCurrentTab('analyst');
              }}
              onNavigateToDatasets={() => setCurrentTab('datasets')}
            />
          )}

          {currentTab === 'datasets' && (
            <DatasetsPage
              datasets={datasets}
              selectedDatasetId={selectedDatasetId}
              onSelectDataset={setSelectedDatasetId}
              onRefreshDatasets={handleRefreshDatasets}
              onNavigateToAnalyst={(datasetId) => {
                setSelectedDatasetId(datasetId);
                setCurrentTab('analyst');
              }}
            />
          )}

          {currentTab === 'analyst' && (
            <AnalystPage
              selectedDatasetId={selectedDatasetId}
              datasets={datasets}
              currentSessionId={currentSessionId}
              onSessionCreated={(id) => {
                setCurrentSessionId(id);
                handleRefreshSessions();
              }}
              initialPrompt={initialPrompt}
              onClearInitialPrompt={() => setInitialPrompt(undefined)}
              onNavigateToReports={(reportId) => {
                setInitialReportId(reportId);
                setCurrentTab('reports');
              }}
            />
          )}

          {currentTab === 'reports' && (
            <ReportsPage
              datasets={datasets}
              selectedDatasetId={selectedDatasetId}
              initialReportId={initialReportId}
              onClearInitialReportId={() => setInitialReportId(undefined)}
            />
          )}
        </main>
      </div>

      {/* Configuration & Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentModel={settingsStatus.model}
        isConfigured={settingsStatus.api_key_configured}
        onSaved={async () => {
          const s = await api.getSettings();
          setSettingsStatus(s);
        }}
      />
    </div>
  );
};

export default App;
