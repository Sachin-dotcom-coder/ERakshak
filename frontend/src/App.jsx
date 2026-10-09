// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import LoginModal from './components/loginmodal';

// Import your existing main view/dashboard
// Adjust the import path if your file is named DashboardView or MainLayout
import DashboardView from './views/DashboardView'; 

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if operator token exists in localStorage
    const token = localStorage.getItem('erakshak_jwt');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (data) => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('erakshak_jwt');
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
        Loading Command Center...
      </div>
    );
  }

  // 1. Show Login Screen if NOT authenticated
  if (!isAuthenticated) {
    return <LoginModal onLoginSuccess={handleLoginSuccess} />;
  }

  // 2. Show Dashboard with Top Bar Logout Button if authenticated
  return (
    <div className="relative min-h-screen bg-slate-950 text-white">
      {/* Logout Overlay Button floating on top-right header */}
      <div className="fixed top-3 right-4 z-50">
        <button
          onClick={handleLogout}
          className="bg-red-500/20 border border-red-500/40 text-red-300 hover:bg-red-600 hover:text-white px-3 py-1 rounded-md text-xs font-semibold transition shadow-lg"
        >
          Logout Operator
        </button>
      </div>

      {/* Main Command Center Dashboard */}
      <DashboardView />
    </div>
  );
}