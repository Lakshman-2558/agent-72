import React from 'react';
import { Shield, ChevronDown, Building2, Calendar, Radio, Sparkles } from 'lucide-react';
import { Institution } from '../../api/types';

interface AgentHeaderProps {
  institutions: Institution[];
  selectedInstitutionId: string;
  onSelectInstitution: (id: string) => void;
  selectedPeriod: string;
  onSelectPeriod: (period: string) => void;
  isConnected: boolean;
  onNavigateTab?: (tab: string) => void;
}

export const AgentHeader: React.FC<AgentHeaderProps> = ({
  institutions,
  selectedInstitutionId,
  onSelectInstitution,
  selectedPeriod,
  onSelectPeriod,
  isConnected,
  onNavigateTab,
}) => {
  const periods = ['2024-2025', '2026-2027', '2023-2024', '2022-2023'];

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-slate-200/90 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Branding */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-sm ring-2 ring-blue-600/20">
            <span className="font-bold text-base tracking-wider">72</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-slate-900 tracking-tight text-base">AGENT 72</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 uppercase tracking-wider">
                Institutional AI
              </span>
            </div>
            <p className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">
              Strategic Planning Agent
            </p>
          </div>
        </div>

        {/* Right: Controls & Badges */}
        <div className="flex items-center gap-3">
          {/* Institution Selector */}
          <div className="relative inline-block">
            <div className="flex items-center gap-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200/90 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 transition-colors shadow-xs">
              <Building2 className="w-3.5 h-3.5 text-slate-500" />
              <select
                value={selectedInstitutionId}
                onChange={(e) => onSelectInstitution(e.target.value)}
                className="bg-transparent font-medium text-slate-800 pr-5 focus:outline-none cursor-pointer appearance-none"
              >
                {institutions.map((inst) => (
                  <option key={inst.id} value={inst.id}>
                    {inst.name} ({inst.code})
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2 pointer-events-none" />
            </div>
          </div>

          {/* Analysis Period Selector */}
          <div className="relative inline-block">
            <div className="flex items-center gap-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200/90 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 transition-colors shadow-xs">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <select
                value={selectedPeriod}
                onChange={(e) => onSelectPeriod(e.target.value)}
                className="bg-transparent font-medium text-slate-800 pr-5 focus:outline-none cursor-pointer appearance-none"
              >
                {periods.map((p) => (
                  <option key={p} value={p}>
                    FY {p}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2 pointer-events-none" />
            </div>
          </div>

          {/* Leadership View Badge */}
          <div className="hidden sm:flex items-center gap-1.5 bg-indigo-50 border border-indigo-200/70 text-indigo-700 text-xs font-semibold px-2.5 py-1.5 rounded-lg shadow-xs">
            <Shield className="w-3.5 h-3.5 text-indigo-600" />
            <span>Leadership View</span>
          </div>

          {/* Live Status Indicator */}
          <div className="flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white">
            <Radio className={`w-3 h-3 ${isConnected ? 'text-emerald-500 animate-pulse' : 'text-slate-400'}`} />
            <span className={isConnected ? 'text-slate-700' : 'text-slate-400'}>
              {isConnected ? 'Live' : 'Connecting'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
