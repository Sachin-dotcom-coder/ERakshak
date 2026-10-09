import React, { useState } from 'react';

interface loginmodalProps {
  onLoginSuccess: (data: { access_token: string; role: string }) => void;
}

export default function loginmodal({ onLoginSuccess }: loginmodalProps) {
  const [email, setEmail] = useState<string>('');
  const [otp, setOtp] = useState<string>('');
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Inside LoginModal.tsx
const handleRequestOtp = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);
  setError('');

  try {
    const res = await fetch('http://127.0.0.1:8000/api/auth/request-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.trim() }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((issue: { msg?: string }) => issue.msg).filter(Boolean).join(', ')
        : data.detail;
      throw new Error(detail || 'Failed to send OTP');
    }
    setStep(2);
  } catch (err: any) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};

const handleVerifyOtp = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);
  setError('');

  try {
    const res = await fetch('http://127.0.0.1:8000/api/auth/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.trim(), otp: otp.trim() }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Verification failed');

    localStorage.setItem('erakshak_jwt', data.access_token);
    onLoginSuccess(data);
  } catch (err: any) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl">
        <h2 className="text-xl font-bold text-white mb-4">🚦 E-Rakshak Portal</h2>
        {error && <div className="text-red-400 text-xs mb-3">{error}</div>}

        {step === 1 ? (
          <form onSubmit={handleRequestOtp} className="space-y-4">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="operator@surat.gov.in"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white"
            />
            <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white py-2 rounded-lg">
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <input
              type="text"
              required
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              placeholder="123456"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-center text-white"
            />
            <button type="submit" disabled={loading} className="w-full bg-emerald-600 text-white py-2 rounded-lg">
              {loading ? 'Verifying...' : 'Verify & Enter'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}