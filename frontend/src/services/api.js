export async function loginOperator(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', 'admin');
  formData.append('password', 'surat_admin_2026');

  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });

  if (!res.ok) throw new Error('Invalid login credentials');
  
  const data = await res.json();
  localStorage.setItem('erakshak_jwt', data.access_token);
  return data;
}

export async function authFetch(url, options = {}) {
  const token = localStorage.getItem('erakshak_jwt');
  
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  const response = await fetch(url, { ...options, headers });
  
  if (response.status === 401) {
    localStorage.removeItem('erakshak_jwt');
    window.location.href = '/login'; // Redirect on token expiry
  }
  
  return response.json();
}

// Note: this module-level WebSocket instantiation is legacy and kept for reference.
// The actual WebSocket connection is managed in useTrafficData.ts via wsUrl().
const token = localStorage.getItem('erakshak_jwt');
const _wsBase = import.meta.env.VITE_API_URL
  ? (import.meta.env.VITE_API_URL.replace(/^https:\/\//, 'wss://').replace(/^http:\/\//, 'ws://'))
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`;
const ws = new WebSocket(`${_wsBase}/api/ws/traffic?token=${token}`);