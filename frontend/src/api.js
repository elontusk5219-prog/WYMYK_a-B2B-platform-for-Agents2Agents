const API_BASE = import.meta.env.VITE_API_BASE || '';

function getApiKey() {
  return localStorage.getItem('a2a_api_key') || '';
}

export function setApiKey(key) {
  if (key) localStorage.setItem('a2a_api_key', key);
  else localStorage.removeItem('a2a_api_key');
}

export function isLoggedIn() {
  return !!getApiKey();
}

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  const key = getApiKey();
  if (key) headers['X-API-Key'] = key;
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    setApiKey('');
    window.dispatchEvent(new Event('a2a:unauthorized'));
    throw new Error('未授权');
  }
  if (!res.ok) {
    const t = await res.text();
    let msg = t;
    try {
      const j = JSON.parse(t);
      msg = j.detail || j.message || t;
    } catch (_) {}
    throw new Error(msg);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get: (path) => request(path, { method: 'GET' }),
  post: (path, body) => request(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  patch: (path, body) => request(path, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
  delete: (path) => request(path, { method: 'DELETE' }),
};

export default api;
