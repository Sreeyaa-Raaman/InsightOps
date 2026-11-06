import React, { useState } from 'react';
import { DatasetPreview } from '../types';
import { Search } from 'lucide-react';

interface DataTableProps {
  preview: DatasetPreview;
}

export const DataTable: React.FC<DataTableProps> = ({ preview }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredRows = preview.rows.filter((row) =>
    Object.values(row).some((val) =>
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
      {/* Table Header controls */}
      <div className="p-3.5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-slate-900 dark:text-white">
            Data Sample Preview
          </span>
          <span className="text-[11px] text-slate-500 ml-2">
            Showing first {preview.rows.length} of {preview.total_rows.toLocaleString()} records ({preview.total_columns} columns)
          </span>
        </div>
        <div className="relative w-56">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search preview records..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full text-xs pl-8 pr-3 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Scrollable Table */}
      <div className="overflow-x-auto max-h-96">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50/80 dark:bg-slate-850 border-b border-slate-200 dark:border-slate-800 sticky top-0">
              <th className="py-2.5 px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-12 text-center">
                #
              </th>
              {preview.columns.map((col) => (
                <th
                  key={col}
                  className="py-2.5 px-3.5 text-[11px] font-semibold text-slate-700 dark:text-slate-300 tracking-wider whitespace-nowrap"
                >
                  <div className="flex items-center space-x-1.5">
                    <span>{col}</span>
                    <span className="text-[9px] font-mono font-normal px-1 py-0.5 rounded bg-slate-200/60 dark:bg-slate-800 text-slate-500">
                      {preview.dtypes[col] || 'any'}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-mono">
            {filteredRows.length === 0 ? (
              <tr>
                <td
                  colSpan={preview.columns.length + 1}
                  className="py-8 text-center text-xs text-slate-400 italic"
                >
                  No matching records found
                </td>
              </tr>
            ) : (
              filteredRows.map((row, idx) => (
                <tr
                  key={idx}
                  className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition"
                >
                  <td className="py-2 px-3 text-center text-slate-400 text-[10px]">
                    {idx + 1}
                  </td>
                  {preview.columns.map((col) => {
                    const val = row[col];
                    const isNull = val === null || val === undefined || val === '';
                    return (
                      <td
                        key={col}
                        className="py-2 px-3.5 whitespace-nowrap text-slate-800 dark:text-slate-200"
                      >
                        {isNull ? (
                          <span className="text-amber-500 dark:text-amber-400/80 italic text-[11px]">
                            null
                          </span>
                        ) : typeof val === 'number' ? (
                          <span className="text-indigo-600 dark:text-indigo-400">
                            {Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2)}
                          </span>
                        ) : (
                          String(val)
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
