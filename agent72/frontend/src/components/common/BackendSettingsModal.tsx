import React, { useState } from 'react';
import { getBackendBaseUrl, saveCustomBackendUrl } from '../../api/client';
import axios from 'axios';

interface BackendSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved: () => void;
}

export const BackendSettingsModal: React.FC<BackendSettingsModalProps> = ({
  isOpen,
  onClose,
  onSaved,
}) => {
  const currentUrl = localStorage.getItem('AGENT72_BACKEND_URL') || import.meta.env.VITE_API_URL || '';
  const [urlInput, setUrlInput] = useState(currentUrl);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  if (!isOpen) return null;

  const handleTestAndSave = async (urlToUse: string) => {
    const cleanUrl = urlToUse.trim().replace(/\/$/, '');
    setTesting(true);
    setTestResult(null);

    try {
      // Test the URL with /health or /api/v1/organizations/institutions
      const targetHealth = cleanUrl ? `${cleanUrl}/health` : '/health';
      const targetApi = cleanUrl ? `${cleanUrl}/api/v1/organizations/institutions` : '/api/v1/organizations/institutions';
      
      let healthy = false;
      let note = '';
      try {
        const res = await axios.get(targetHealth, { timeout: 15000 });
        if (res.data?.status === 'healthy' || res.status === 200) {
          healthy = true;
          note = 'Health check passed!';
        }
      } catch {
        // Fallback to testing organizations endpoint
        const res2 = await axios.get(targetApi, { timeout: 15000 });
        if (res2.data?.items || Array.isArray(res2.data)) {
          healthy = true;
          note = 'API endpoint responded successfully!';
        }
      }

      if (healthy) {
        saveCustomBackendUrl(cleanUrl);
        setTestResult({ success: true, message: `Connected successfully! ${note}` });
        setTimeout(() => {
          onSaved();
          onClose();
        }, 800);
      } else {
        setTestResult({
          success: false,
          message: 'Server reached, but did not respond with expected Agent 72 payload.',
        });
      }
    } catch (err: any) {
      setTestResult({
        success: false,
        message:
          err.message?.includes('Network Error') || err.code === 'ERR_NETWORK'
            ? 'Network error. Make sure CORS_ORIGINS on your backend allows this domain, and your Render service is awake.'
            : `Connection failed: ${err.message || 'Unknown error'}`,
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSaveDirect = () => {
    saveCustomBackendUrl(urlInput.trim());
    onSaved();
    onClose();
  };

  const handleReset = () => {
    saveCustomBackendUrl(null);
    setUrlInput(import.meta.env.VITE_API_URL || '');
    onSaved();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="bg-gradient-to-r from-brand-900 to-brand-800 p-6 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center border border-white/20">
              <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-lg leading-tight">Backend API Connection</h3>
              <p className="text-xs text-brand-200">Connect frontend to your live Render backend</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/70 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">
              Backend Service URL
            </label>
            <div className="relative">
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://agent-72-backend.onrender.com"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm font-mono text-slate-800 placeholder:text-slate-400"
              />
            </div>
            <p className="text-xs text-slate-500 mt-1.5">
              Enter the URL of your Render backend. In production builds, this can also be set via{' '}
              <code className="bg-slate-100 px-1 py-0.5 rounded text-brand-700">VITE_API_URL</code> on Vercel.
            </p>
          </div>

          {testResult && (
            <div
              className={`p-3.5 rounded-xl text-xs flex items-start gap-2.5 ${
                testResult.success
                  ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
                  : 'bg-rose-50 border border-rose-200 text-rose-800'
              }`}
            >
              {testResult.success ? (
                <svg className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
              <div className="leading-relaxed">{testResult.message}</div>
            </div>
          )}

          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs text-slate-600 space-y-1">
            <div className="font-semibold text-slate-700">Current Active Base URL:</div>
            <div className="font-mono text-slate-800 break-all">{getBackendBaseUrl()}</div>
          </div>
        </div>

        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-2">
          <button
            onClick={handleReset}
            type="button"
            className="text-xs text-slate-600 hover:text-slate-900 underline px-2 py-1.5"
          >
            Reset to default
          </button>
          <div className="flex items-center gap-2">
            <button
              onClick={handleSaveDirect}
              type="button"
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-100 transition-colors"
            >
              Save Without Test
            </button>
            <button
              onClick={() => handleTestAndSave(urlInput)}
              disabled={testing}
              type="button"
              className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 transition-colors shadow-sm disabled:opacity-50 flex items-center gap-1.5"
            >
              {testing ? (
                <>
                  <svg className="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Testing...
                </>
              ) : (
                'Test & Connect'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
