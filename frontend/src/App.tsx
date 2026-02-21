import { useState } from 'react';
import TransactionParser from './components/TransactionParser';
import TransactionValidator from './components/TransactionValidator';
import TransactionFilter from './components/TransactionFilter';
import ReturnsCalculator from './components/ReturnsCalculator';
import PerformanceDashboard from './components/PerformanceDashboard';
import './App.css';

const TABS = [
  { id: 'parse', label: 'Parser', component: TransactionParser },
  { id: 'validator', label: 'Validator', component: TransactionValidator },
  { id: 'filter', label: 'Filter', component: TransactionFilter },
  { id: 'returns', label: 'Returns', component: ReturnsCalculator },
  { id: 'performance', label: 'Performance', component: PerformanceDashboard },
] as const;

function App() {
  const [activeTab, setActiveTab] = useState('parse');
  const ActiveComponent = TABS.find(t => t.id === activeTab)?.component ?? TransactionParser;

  return (
    <div className="app">
      <header>
        <h1>BlackRock Retirement Savings API</h1>
        <p className="subtitle">Interactive Playground — Expense-Based Micro-Investment System</p>
      </header>

      <nav className="tabs">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main>
        <ActiveComponent />
      </main>

      <footer>
        <p>
          API Docs: <a href="/docs" target="_blank" rel="noopener">/docs</a>
          {' | '}
          v1.0.0
        </p>
      </footer>
    </div>
  );
}

export default App
