import { useState } from 'react';
import { api } from '../api/client';

const SAMPLE = JSON.stringify([
  { date: "2023-10-12 20:15:30", amount: 250 },
  { date: "2023-02-28 15:49:20", amount: 375 },
  { date: "2023-07-01 21:59:00", amount: 620 },
  { date: "2023-12-17 08:09:45", amount: 480 },
], null, 2);

export default function TransactionParser() {
  const [input, setInput] = useState(SAMPLE);
  const [output, setOutput] = useState<string>('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');
    setLoading(true);
    try {
      const data = JSON.parse(input);
      const result = await api.parse(data);
      setOutput(JSON.stringify(result, null, 2));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="endpoint-card">
      <h2>Transaction Parser</h2>
      <p className="endpoint-path">POST /transactions:parse</p>
      <p className="description">Parse expenses into transactions with ceiling and remanent.</p>
      <div className="io-container">
        <div className="io-panel">
          <label>Input (Expenses JSON)</label>
          <textarea value={input} onChange={e => setInput(e.target.value)} rows={12} />
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
