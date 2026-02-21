/**
 * API client — all calls use relative paths (same origin, no CORS needed).
 */

const BASE = '/blackrock/challenge/v1';

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  parse: (expenses: unknown) => request('POST', '/transactions:parse', expenses),
  validate: (data: unknown) => request('POST', '/transactions:validator', data),
  filter: (data: unknown) => request('POST', '/transactions:filter', data),
  returnsNps: (data: unknown) => request('POST', '/returns:nps', data),
  returnsIndex: (data: unknown) => request('POST', '/returns:index', data),
  performance: () => request('GET', '/performance'),
};
