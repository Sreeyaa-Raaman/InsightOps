import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileSpreadsheet, 
  Database, 
  AlertCircle, 
  Loader2, 
  CheckCircle2, 
  MessageSquare,
  FileCheck
} from 'lucide-react';
import { api } from '../services/api';
import { DatasetListItem, DatasetOverview, DatasetPreview } from '../types';
import { DataTable } from '../components/DataTable';

interface DatasetsPageProps {
  datasets: DatasetListItem[];
  selectedDatasetId: string;
  onSelectDataset: (id: string) => void;
  onRefreshDatasets: () => void;
  onNavigateToAnalyst: (datasetId: string) => void;
}

export const DatasetsPage: React.FC<DatasetsPageProps> = ({
  datasets,
  selectedDatasetId,
  onSelectDataset,
  onRefreshDatasets,
  onNavigateToAnalyst,
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const [overview, setOverview] = useState<DatasetOverview | null>(null);
  const [preview, setPreview] = useState<DatasetPreview | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    if (selectedDatasetId) {
      loadDatasetDetails(selectedDatasetId);
    }
  }, [selectedDatasetId]);

  const loadDatasetDetails = async (id: string) => {
    setLoadingDetails(true);
    try {
      const [ov, prev] = await Promise.all([
        api.getDatasetOverview(id),
        api.getDatasetPreview(id, 15)
      ]);
      setOverview(ov);
      setPreview(prev);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const processFile = async (file: File) => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!['.csv', '.xlsx', '.xls'].includes(ext)) {
      setUploadError("Invalid format. Please upload a .csv, .xlsx, or .xls file.");
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setUploadError("File size exceeds 50MB limit.");
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const newDataset = await api.uploadDataset(file);
      setUploadSuccess(`Uploaded "${newDataset.original_name}" successfully (${newDataset.row_count.toLocaleString()} rows).`);
      onRefreshDatasets();
      onSelectDataset(newDataset.id);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload dataset.');
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFile(files[0]);
      e.target.value = '';
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            Dataset Library & Schema Inspector
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Review column attributes, data completeness, unique distributions, and interactive sample records.
          </p>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`relative p-8 rounded-2xl border-2 border-dashed transition-all text-center flex flex-col items-center justify-center cursor-pointer ${
          isDragging
            ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/40 scale-[1.005]'
            : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-700'
        }`}
      >
        <input
          type="file"
          id="file-drop-input"
          accept=".csv, .xlsx, .xls"
          onChange={handleFileUpload}
          disabled={uploading}
          className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
        />
        <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-3">
          {uploading ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : (
            <Upload className="w-6 h-6" />
          )}
        </div>
        <h4 className="text-xs font-semibold text-slate-900 dark:text-white">
          {uploading ? 'Parsing and inspecting dataset schema...' : 'Drag and drop your dataset here, or browse files'}
        </h4>
        <p className="text-[11px] text-slate-400 mt-1">
          Supports CSV (.csv) and Excel (.xlsx, .xls) up to 50MB
        </p>
      </div>

      {/* Upload Alerts */}
      {uploadError && (
        <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}
      {uploadSuccess && (
        <div className="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{uploadSuccess}</span>
        </div>
      )}

      {/* Dataset Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {datasets.map((d) => {
          const isSelected = d.id === selectedDatasetId;
          return (
            <div
              key={d.id}
              onClick={() => onSelectDataset(d.id)}
              className={`p-4.5 rounded-2xl border transition cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? 'border-indigo-600 bg-indigo-50/40 dark:bg-indigo-950/30 shadow-xs ring-1 ring-indigo-500/20'
                  : 'border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300'
              }`}
            >
              <div>
                <div className="flex items-center space-x-2.5 mb-2.5">
                  <div className={`p-2 rounded-xl ${isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500'}`}>
                    <FileSpreadsheet className="w-4 h-4" />
                  </div>
                  <h4 className="text-xs font-semibold text-slate-900 dark:text-white truncate">
                    {d.original_name}
                  </h4>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-500 my-2.5 bg-slate-50/80 dark:bg-slate-850/80 p-2.5 rounded-xl">
                  <div>
                    <span className="block text-[10px] text-slate-400">Total Observations</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">
                      {d.row_count.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-400">Attributes</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">
                      {d.column_count} columns
                    </span>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <span className="text-[10px] font-mono text-slate-400">
                  {(d.file_size_bytes / 1024).toFixed(1)} KB
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onNavigateToAnalyst(d.id);
                  }}
                  className="flex items-center space-x-1 text-xs text-indigo-600 dark:text-indigo-400 hover:underline font-semibold cursor-pointer"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Analyze</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Dataset Details & Schema Inspector */}
      {loadingDetails ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 text-xs">
          <Loader2 className="w-6 h-6 animate-spin text-indigo-600 mb-2" />
          <span>Extracting column metadata and generating preview...</span>
        </div>
      ) : overview && preview ? (
        <div className="space-y-6">
          {/* Schema Metadata Table */}
          <div className="p-6 rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3.5">
              Attribute Specifications & Data Types ({overview.columns.length} columns)
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 text-[11px]">
                    <th className="py-2.5 px-3">Column Name</th>
                    <th className="py-2.5 px-3">Data Type</th>
                    <th className="py-2.5 px-3">Non-Null Records</th>
                    <th className="py-2.5 px-3">Completeness</th>
                    <th className="py-2.5 px-3">Unique Values</th>
                    <th className="py-2.5 px-3">Sample Values</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-mono text-[11px]">
                  {overview.columns.map((col) => {
                    const completeness = overview.row_count > 0 ? (col.non_null_count / overview.row_count) * 100 : 100;
                    return (
                      <tr key={col.name} className="hover:bg-slate-50/70 dark:hover:bg-slate-850/60">
                        <td className="py-2.5 px-3 font-semibold text-slate-800 dark:text-slate-200 font-sans">
                          {col.name}
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-[10px]">
                            {col.dtype}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-600 dark:text-slate-400">
                          {col.non_null_count.toLocaleString()}
                        </td>
                        <td className="py-2.5 px-3">
                          <div className="flex items-center space-x-2 w-28">
                            <div className="flex-1 h-1.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                              <div
                                className={`h-full rounded-full ${completeness >= 98 ? 'bg-emerald-500' : completeness >= 90 ? 'bg-indigo-500' : 'bg-amber-500'}`}
                                style={{ width: `${completeness}%` }}
                              ></div>
                            </div>
                            <span className="text-[10px] text-slate-500">{completeness.toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="py-2.5 px-3 text-slate-600 dark:text-slate-400">
                          {col.unique_count.toLocaleString()}
                        </td>
                        <td className="py-2.5 px-3 text-slate-500 font-sans truncate max-w-xs">
                          {col.sample_values?.slice(0, 3).map(String).join(', ') || '-'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Interactive Data Preview Table */}
          <DataTable preview={preview} />
        </div>
      ) : null}
    </div>
  );
};
