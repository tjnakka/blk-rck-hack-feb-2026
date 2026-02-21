import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { PerformanceResponse } from '../types';

export default function PerformanceDashboard() {
  const [metrics, setMetrics] = useState<PerformanceResponse | null>(null);
  const [error, setError] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchMetrics = async () => {
    try {
      const data = await api.performance() as PerformanceResponse;
      setMetrics(data);
      setError('');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  return (
    <div className="endpoint-card">
      <h2>Performance Dashboard</h2>
      <p className="endpoint-path">GET /performance</p>
      <p className="description">System execution metrics: uptime, memory, threads.</p>
      {metrics && (
        <div className="metrics-grid">
          <div className="metric">
            <span className="metric-label">Uptime</span>
            <span className="metric-value">{metrics.time}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Memory</span>
            <span className="metric-value">{metrics.memory}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Threads</span>
            <span className="metric-value">{metrics.threads}</span>
          </div>
        </div>
      )}
      {error && <div className="error">{error}</div>}
      <div className="button-group">
        <button onClick={fetchMetrics}>Refresh</button>
        <label className="toggle">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={e => setAutoRefresh(e.target.checked)}
          />
          Auto-refresh (2s)
        </label>
      </div>
    </div>
  );
}
