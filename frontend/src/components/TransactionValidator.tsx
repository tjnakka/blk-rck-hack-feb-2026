import { useState } from 'react';
import { api } from '../api/client';

const SAMPLE = JSON.stringify({
  wage: 50000,
  transactions: [
    { date: "2023-01-15 10:30:00", amount: 2000, ceiling: 300, remanent: 50 },
    { date: "2023-03-20 14:45:00", amount: 3500, ceiling: 400, remanent: 70 },
    { date: "2023-06-10 09:15:00", amount: 1500, ceiling: 200, remanent: 30 },
    { date: "2023-07-10 09:15:00", amount: -250, ceiling: 200, remanent: 30 },
  ],
}, null, 2);

export default function TransactionValidator() {
  const [input, setInput] = useState(SAMPLE);
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');
    setLoading(true);
    try {
      const data = JSON.parse(input);
      const result = await api.validate(data);
      setOutput(JSON.stringify(result, null, 2));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="endpoint-card">
      <h2>Transaction Validator</h2>
      <p className="endpoint-path">POST /transactions:validator</p>
      <p className="description">Validate transactions: reject negative amounts and duplicates.</p>
      <div className="io-container">
        <div className="io-panel">
          <label>Input</label>
          <textarea value={input} onChange={e => setInput(e.target.value)} rows={14} />
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
