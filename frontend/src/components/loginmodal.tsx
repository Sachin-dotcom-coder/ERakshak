import React, { useState } from 'react';
import { KeyRound, Mail, AlertCircle, Loader2 } from 'lucide-react';
import { SuratTrafficNexusLogo } from './traffic/Logo';

interface loginmodalProps {
  onLoginSuccess: (data: { access_token: string; role: string }) => void;
}

export default function loginmodal({ onLoginSuccess }: loginmodalProps) {
  const [email, setEmail] = useState<string>('');
  const [otp, setOtp] = useState<string>('');
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

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
      localStorage.setItem('erakshak_operator_email', email.trim());
      onLoginSuccess(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-background flex items-center justify-center z-50 p-4 font-sans text-foreground">
      {/* Tactical Background Effects */}
      <div className="absolute inset-0 pending-grid opacity-20 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background pointer-events-none" />
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent animate-scan" />

      <div className="relative w-full max-w-sm panel-glass p-8 overflow-hidden shadow-2xl">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-primary/40" />

        <div className="flex flex-col items-center mb-8">
          <div className="mb-4">
            <SuratTrafficNexusLogo showBadge />
          </div>
          <h2 className="text-xl font-bold tracking-tight text-foreground uppercase">E-Rakshak Portal</h2>
          <p className="label-xs text-muted-foreground mt-2">Traffic Intelligence Core v2.0</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-destructive shrink-0" />
            <p className="text-destructive text-xs font-medium">{error}</p>
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleRequestOtp} className="space-y-5">
            <div className="space-y-1.5">
              <label className="label-xs text-muted-foreground ml-1">Operator ID / Email</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="operator@surat.gov.in"
                  className="w-full bg-panel border border-border rounded-md pl-9 pr-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all font-mono"
                />
              </div>
            </div>
            
            <button 
              type="submit" 
              disabled={loading} 
              className="w-full bg-primary text-primary-foreground font-semibold text-sm py-2 rounded-md transition-colors hover:bg-primary/90 active:scale-[0.98] flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>AUTHENTICATE</span>}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-5 animate-in fade-in slide-in-from-right-4 duration-300">
            <div className="space-y-1.5 text-center">
              <label className="label-xs text-muted-foreground">Authorization Code</label>
              <div className="relative mx-auto mt-2">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <KeyRound className="h-4 w-4 text-muted-foreground" />
                </div>
                <input
                  type="text"
                  required
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  placeholder="------"
                  className="w-full bg-panel border border-border rounded-md pl-10 pr-3 py-2.5 text-lg text-center tracking-[0.6em] font-mono text-primary placeholder:text-muted-foreground focus:outline-none focus:border-[#22c55e]/50 focus:ring-1 focus:ring-[#22c55e]/50 transition-all"
                />
              </div>
            </div>
            
            <button 
              type="submit" 
              disabled={loading || otp.length < 6} 
              className="w-full bg-[#22c55e] text-black font-semibold text-sm py-2 rounded-md transition-colors hover:bg-[#22c55e]/90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>VERIFY ACCESS</span>}
            </button>
            
            <button 
              type="button" 
              onClick={() => setStep(1)}
              className="w-full text-xs label-xs text-muted-foreground hover:text-foreground transition-colors mt-2"
            >
              [ CANCEL ]
            </button>
          </form>
        )}
      </div>
    </div>
  );
}