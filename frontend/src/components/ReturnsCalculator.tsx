import { useState } from 'react';
import { api } from '../api/client';

const SAMPLE = JSON.stringify({
  age: 29,
  wage: 50000,
  inflation: 5.5,
  q: [{ fixed: 0, start: "2023-07-01 00:00:00", end: "2023-07-31 23:59:59" }],
  p: [{ extra: 25, start: "2023-10-01 08:00:00", end: "2023-12-31 19:59:59" }],
  k: [
    { start: "2023-01-01 00:00:00", end: "2023-12-31 23:59:59" },
    { start: "2023-03-01 00:00:00", end: "2023-11-30 23:59:59" },
  ],
  transactions: [
    { date: "2023-02-28 15:49:20", amount: 375 },
    { date: "2023-07-01 21:59:00", amount: 620 },
    { date: "2023-10-12 20:15:30", amount: 250 },
    { date: "2023-12-17 08:09:45", amount: 480 },
    { date: "2023-12-17 08:09:45", amount: -10 },
  ],
}, null, 2);

export default function ReturnsCalculator() {
  const [input, setInput] = useState(SAMPLE);
  const [outputNps, setOutputNps] = useState('');
  const [outputIndex, setOutputIndex] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (type: 'nps' | 'index') => {
    setError('');
    setLoading(true);
    try {
      const data = JSON.parse(input);
      if (type === 'nps') {
        const result = await api.returnsNps(data);
        setOutputNps(JSON.stringify(result, null, 2));
      } else {
        const result = await api.returnsIndex(data);
        setOutputIndex(JSON.stringify(result, null, 2));
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleBoth = async () => {
    setError('');
    setLoading(true);
    try {
      const data = JSON.parse(input);
      const [nps, index] = await Promise.all([
        api.returnsNps(data),
        api.returnsIndex(data),
      ]);
      setOutputNps(JSON.stringify(nps, null, 2));
      setOutputIndex(JSON.stringify(index, null, 2));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="endpoint-card">
      <h2>Returns Calculator</h2>
      <p className="endpoint-path">POST /returns:nps &amp; /returns:index</p>
      <p className="description">Calculate investment returns with compound interest and inflation adjustment.</p>
      <div className="io-container">
        <div className="io-panel">
          <label>Input</label>
          <textarea value={input} onChange={e => setInput(e.target.value)} rows={22} />
        </div>
        <div className="io-panel io-panel-split">
          <div>
            <label>NPS (7.11%)</label>
            <pre>{outputNps || 'Run to see NPS output'}</pre>
          </div>
          <div>
            <label>Index / NIFTY 50 (14.49%)</label>
            <pre>{outputIndex || 'Run to see Index output'}</pre>
          </div>
        </div>
      </div>
      {error && <div className="error">{error}</div>}
      <div className="button-group">
        <button onClick={() => handleSubmit('nps')} disabled={loading}>Run NPS</button>
        <button onClick={() => handleSubmit('index')} disabled={loading}>Run Index</button>
        <button onClick={handleBoth} disabled={loading} className="primary">
          {loading ? 'Running...' : 'Run Both'}
        </button>
      </div>
    </div>
  );
}
