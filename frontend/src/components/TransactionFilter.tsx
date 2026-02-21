import { useState } from 'react';
import { api } from '../api/client';

const SAMPLE = JSON.stringify({
  q: [{ fixed: 0, start: "2023-07-01 00:00:00", end: "2023-07-31 23:59:59" }],
  p: [{ extra: 30, start: "2023-10-01 00:00:00", end: "2023-12-31 23:59:59" }],
  k: [{ start: "2023-01-01 00:00:00", end: "2023-12-31 23:59:59" }],
  wage: 50000,
  transactions: [
    { date: "2023-02-28 15:49:20", amount: 375 },
    { date: "2023-07-15 10:30:00", amount: 620 },
    { date: "2023-10-12 20:15:30", amount: 250 },
    { date: "2023-10-12 20:15:30", amount: 250 },
    { date: "2023-12-17 08:09:45", amount: -480 },
  ],
}, null, 2);

export default function TransactionFilter() {
  const [input, setInput] = useState(SAMPLE);
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');
    setLoading(true);
    try {
      const data = JSON.parse(input);
      const result = await api.filter(data);
      setOutput(JSON.stringify(result, null, 2));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="endpoint-card">
      <h2>Transaction Filter</h2>
      <p className="endpoint-path">POST /transactions:filter</p>
      <p className="description">Filter transactions by temporal constraints (q, p, k periods).</p>
      <div className="io-container">
        <div className="io-panel">
          <label>Input</label>
          <textarea value={input} onChange={e => setInput(e.target.value)} rows={18} />
        </div>
        <div className="io-panel">
          <label>Output</label>
          <pre>{output || 'Click "Run" to see output'}</pre>
        </div>
      </div>
      {error && <div className="error">{error}</div>}
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Running...' : 'Run'}
      </button>
    </div>
  );
}
