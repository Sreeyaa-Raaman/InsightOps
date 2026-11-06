import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { ChartConfig } from '../types';
import { BarChart3, TrendingUp, PieChart as PieIcon, ScatterChart as ScatterIcon } from 'lucide-react';

interface ChartRendererProps {
  config: ChartConfig;
}

const PALETTE = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#3b82f6'];

export const ChartRenderer: React.FC<ChartRendererProps> = ({ config }) => {
  if (!config || !config.data || config.data.length === 0) {
    return null;
  }

  const { chart_type, title, x_key, y_keys = [], data, x_label, y_label, description } = config;

  const getChartIcon = () => {
    switch (chart_type) {
      case 'pie':
        return <PieIcon className="w-4 h-4 text-amber-500" />;
      case 'line':
        return <TrendingUp className="w-4 h-4 text-emerald-500" />;
      case 'scatter':
        return <ScatterIcon className="w-4 h-4 text-purple-500" />;
      default:
        return <BarChart3 className="w-4 h-4 text-indigo-500" />;
    }
  };

  return (
    <div className="my-4 rounded-xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900/90 shadow-xs overflow-hidden transition-all">
      {/* Chart Header */}
      <div className="px-4 py-3 bg-slate-50/70 dark:bg-slate-850/60 border-b border-slate-200/70 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getChartIcon()}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 dark:text-white tracking-tight">
              {title}
            </h4>
            {description && (
              <p className="text-[10px] text-slate-500 dark:text-slate-400">
                {description}
              </p>
            )}
          </div>
        </div>
        <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-slate-200/60 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
          {data.length} records
        </span>
      </div>

      {/* Chart Canvas */}
      <div className="h-68 w-full p-3 pt-4">
        <ResponsiveContainer width="100%" height="100%">
          {chart_type === 'pie' ? (
            <PieChart>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.95)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  color: '#fff',
                  fontSize: '11px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)'
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
              <Pie
                data={data}
                dataKey={y_keys[0] || 'value'}
                nameKey={x_key || 'name'}
                cx="50%"
                cy="50%"
                outerRadius={85}
                innerRadius={42}
                paddingAngle={3}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                labelLine={false}
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} stroke="transparent" />
                ))}
              </Pie>
            </PieChart>
          ) : chart_type === 'line' ? (
            <LineChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" opacity={0.15} />
              <XAxis
                dataKey={x_key}
                tick={{ fontSize: 10, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1', opacity: 0.4 }}
                tickLine={false}
                label={x_label ? { value: x_label, position: 'bottom', offset: 0, fontSize: 10, fill: '#64748b' } : undefined}
              />
              <YAxis
                tick={{ fontSize: 10, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1', opacity: 0.4 }}
                tickLine={false}
                label={y_label ? { value: y_label, angle: -90, position: 'insideLeft', fontSize: 10, fill: '#64748b' } : undefined}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.95)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  color: '#fff',
                  fontSize: '11px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)'
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
              {y_keys.map((key, i) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={PALETTE[i % PALETTE.length]}
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: PALETTE[i % PALETTE.length] }}
                  activeDot={{ r: 5 }}
                />
              ))}
            </LineChart>
          ) : chart_type === 'scatter' ? (
            <ScatterChart margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" opacity={0.15} />
              <XAxis
                dataKey={x_key}
                name={x_label || x_key}
                tick={{ fontSize: 10, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1', opacity: 0.4 }}
                tickLine={false}
                label={x_label ? { value: x_label, position: 'bottom', offset: 0, fontSize: 10, fill: '#64748b' } : undefined}
              />
              <YAxis
                dataKey={y_keys[0]}
                name={y_label || y_keys[0]}
                tick={{ fontSize: 10, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1', opacity: 0.4 }}
                tickLine={false}
                label={y_label ? { value: y_label, angle: -90, position: 'insideLeft', fontSize: 10, fill: '#64748b' } : undefined}
              />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.95)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  color: '#fff',
                  fontSize: '11px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)'
                }}
              />
              <Scatter name={title} data={data} fill="#6366f1" />
            </ScatterChart>
          ) : (
            /* Bar Chart with clean rounded corners */
            <BarChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6366f1" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#4f46e5" stopOpacity={0.8} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" opacity={0.15} vertical={false} />
              <XAxis
                dataKey={x_key}
                tick={{ fontSize: 10, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1', opacity: 0.4 }}
                tickLine={false}
                label={x_label ? { value: x_label, position: 'bottom', offset: 0, fontSize: 10, fill: '#64748b' } : undefined}
              />
              <YAxis
                tick={{ fontSize: 10, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1', opacity: 0.4 }}
                tickLine={false}
                label={y_label ? { value: y_label, angle: -90, position: 'insideLeft', fontSize: 10, fill: '#64748b' } : undefined}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.95)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  color: '#fff',
                  fontSize: '11px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)'
                }}
              />
              {y_keys.length > 1 && <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />}
              {y_keys.map((key, i) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={i === 0 ? "url(#barGradient)" : PALETTE[i % PALETTE.length]}
                  radius={[5, 5, 0, 0]}
                  maxBarSize={50}
                />
              ))}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};
