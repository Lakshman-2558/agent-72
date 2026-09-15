import React from 'react';
import { Institution } from '../../api/types';
import { Building2, Calendar, RotateCcw } from 'lucide-react';

import vignanHeaderLogo from '../../assets/vignan_header_logo.png';
import vignanAccreditations from '../../assets/vignan_accreditations.png';

interface VignanHeaderProps {
  institutions: Institution[];
  selectedInstitutionId: string;
  onSelectInstitution: (id: string) => void;
  selectedPeriod: string;
  onSelectPeriod: (period: string) => void;
  isConnected?: boolean;
  onRefresh?: () => void;
  onOpenAskAgent?: () => void;
  onOpenBackendSettings?: () => void;
  activeTab?: string;
}

export const VignanHeader: React.FC<VignanHeaderProps> = ({
  institutions,
  selectedInstitutionId,
  onSelectInstitution,
  selectedPeriod,
  onSelectPeriod,
  isConnected = true,
  onRefresh,
}) => {
  const periods = ['2024-2025', '2025-2026', '2026-2027', '2023-2024'];

  return (
    <header className="bg-white border-b border-[#D7E4EE] shadow-xs sticky top-0 z-30 select-none">
      {/* Top Banner with Official Imagery */}
      <div className="max-w-[1600px] mx-auto px-3 sm:px-6 py-2 flex flex-col md:flex-row items-center justify-between gap-2.5">
        {/* Left: Official Vignan's University Image (Decreased Size as requested) */}
        <div className="flex items-center select-none shrink-0">
          <img
            src={vignanHeaderLogo}
            alt="Vignan's Foundation for Science, Technology & Research"
            className="h-10 sm:h-11 md:h-12 w-auto object-contain shrink-0"
          />
        </div>

        {/* Right: Institutional Controls, Agent Status & NAAC A++ component at the very last */}
        <div className="flex flex-wrap items-center justify-center md:justify-end gap-2 sm:gap-3 w-full md:w-auto">
          {/* Institution Selector */}
          <div className="relative inline-flex items-center gap-1 bg-[#F5F9FC] hover:bg-white border border-[#D7E4EE] rounded-lg px-2.5 py-1 text-xs text-[#19324A] transition shadow-2xs">
            <Building2 className="w-3.5 h-3.5 text-[#2F6EA6] shrink-0" />
            <select
              value={selectedInstitutionId}
              onChange={(e) => onSelectInstitution(e.target.value)}
              className="bg-transparent font-semibold text-[11px] text-[#19324A] focus:outline-none cursor-pointer max-w-[130px] sm:max-w-[170px] truncate"
            >
              {institutions.map((inst) => (
                <option key={inst.id} value={inst.id}>
                  {inst.name} ({inst.code})
                </option>
              ))}
            </select>
          </div>

          {/* Academic Period Selector */}
          <div className="relative inline-flex items-center gap-1 bg-[#F5F9FC] hover:bg-white border border-[#D7E4EE] rounded-lg px-2.5 py-1 text-xs text-[#19324A] transition shadow-2xs">
            <Calendar className="w-3.5 h-3.5 text-[#2F6EA6] shrink-0" />
            <select
              value={selectedPeriod}
              onChange={(e) => onSelectPeriod(e.target.value)}
              className="bg-transparent font-semibold text-[11px] text-[#19324A] focus:outline-none cursor-pointer"
            >
              {periods.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>

          {/* Refresh */}
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-1.5 rounded-lg border border-[#D7E4EE] bg-[#F5F9FC] hover:bg-white text-[#6B7F91] hover:text-[#163A63] transition shadow-2xs cursor-pointer"
              title="Refresh analytical snapshots"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Agent Status Badge: Does not expose backend URL */}
          <div
            className={`flex items-center gap-2 text-[11px] font-bold px-3 py-1 rounded-lg border select-none transition-all ${isConnected
              ? 'border-emerald-300 bg-emerald-50 text-emerald-800 shadow-2xs'
              : 'border-rose-300 bg-rose-50 text-rose-800 shadow-2xs animate-pulse'
              }`}
            title={isConnected ? 'Agent 72 Status: Active & Operational' : 'Agent 72 Status: Inactive'}
          >
            <span className="relative flex h-2.5 w-2.5">
              {isConnected ? (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-600" />
                </>
              ) : (
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-600" />
              )}
            </span>
            <span className="tracking-tight">{isConnected ? 'Agent Active' : 'Agent Inactive'}</span>
          </div>

          {/* Official NAAC A++ & Global Accreditations Image placed at the very last */}
          <div className="flex items-center shrink-0 pl-1 border-l border-slate-200">
            <img
              src={vignanAccreditations}
              alt="NAAC A+, NIRF, NBA, AICTE, UGC 12(B), DSIR, QS I-GAUGE"
              className="h-8 sm:h-9 md:h-10 w-auto object-contain shrink-0 select-none drop-shadow-2xs"
            />
          </div>
        </div>
      </div>
    </header>
  );
};

