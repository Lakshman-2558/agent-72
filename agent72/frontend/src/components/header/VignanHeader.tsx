import React from 'react';
import { Institution } from '../../api/types';
import { Building2, Calendar, Radio, RotateCcw, Sparkles } from 'lucide-react';

import vignanHeaderLogo from '../../assets/vignan_header_logo.png';
import vignanAccreditations from '../../assets/vignan_accreditations.png';
import agent72Robot from '../../assets/agent72-robot.png';

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
  onOpenAskAgent,
  onOpenBackendSettings,
  activeTab,
}) => {
  const periods = ['2024-2025', '2025-2026', '2026-2027', '2023-2024'];

  return (
    <header className="bg-white border-b border-[#D7E4EE] shadow-xs sticky top-0 z-30 select-none">
      {/* Top Banner with Official Uploaded Imagery */}
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 py-2 flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Left: Official Vignan's University Image */}
        <div className="flex items-center select-none shrink-0">
          <img
            src={vignanHeaderLogo}
            alt="Vignan's Foundation for Science, Technology & Research"
            className="h-11 sm:h-13 md:h-14 w-auto object-contain shrink-0"
          />
        </div>

        {/* Center: CSE PRESENTS / AGENTIC AI DAY 2026 */}
        <div className="text-center py-0.5 select-none shrink-0">
          <div className="text-[10px] sm:text-[11px] font-bold tracking-[0.25em] text-[#6B7F91] uppercase">
            CSE PRESENTS
          </div>
          <h1 className="text-xl sm:text-2xl lg:text-[25px] font-black tracking-wide text-[#163A63] uppercase leading-tight">
            AGENTIC AI DAY 2026
          </h1>
        </div>

        {/* Right: Official Accreditations Strip Image & Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Official Accreditations Image provided by user */}
          <img
            src={vignanAccreditations}
            alt="NAAC A+, NIRF, NBA, AICTE, UGC 12(B), DSIR, QS I-GAUGE"
            className="hidden xl:block h-8 sm:h-9 md:h-10 w-auto object-contain shrink-0 select-none"
          />

          {/* Institutional Controls */}
          <div className="flex items-center gap-1.5 pl-2 border-l border-slate-200">
            {/* Institution Selector */}
            <div className="relative inline-flex items-center gap-1 bg-[#F5F9FC] hover:bg-white border border-[#D7E4EE] rounded-lg px-2 py-1 text-xs text-[#19324A] transition shadow-2xs">
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
            <div className="relative inline-flex items-center gap-1 bg-[#F5F9FC] hover:bg-white border border-[#D7E4EE] rounded-lg px-2 py-1 text-xs text-[#19324A] transition shadow-2xs">
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
                className="p-1.5 rounded-lg border border-[#D7E4EE] bg-[#F5F9FC] hover:bg-white text-[#6B7F91] hover:text-[#163A63] transition shadow-2xs"
                title="Refresh analytical snapshots"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            )}

            {/* Online/Backend Status */}
            <button
              onClick={onOpenBackendSettings}
              type="button"
              className={`flex items-center gap-1.5 text-[10px] font-semibold px-2.5 py-1 rounded-lg border transition-all cursor-pointer ${
                isConnected
                  ? 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                  : 'border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100 animate-pulse'
              }`}
              title="Click to configure or test Backend API URL"
            >
              <Radio className={`w-2.5 h-2.5 ${isConnected ? 'text-emerald-600' : 'text-amber-600'}`} />
              <span>{isConnected ? 'API Connected' : 'Connect Backend'}</span>
            </button>

            {/* Special, Unique & Innovative "Ask Agent 72" Header Button */}
            {onOpenAskAgent && (
              <button
                onClick={onOpenAskAgent}
                className={`relative group flex items-center gap-2 pl-1.5 pr-3 py-1 rounded-full border transition-all duration-300 shadow-xs cursor-pointer ${
                  activeTab === 'ask'
                    ? 'bg-gradient-to-r from-[#163A63] via-indigo-700 to-purple-800 text-white border-indigo-400 shadow-indigo-500/25 ring-2 ring-indigo-300/30'
                    : 'bg-gradient-to-r from-slate-900 via-indigo-950 to-[#163A63] hover:from-blue-900 hover:via-indigo-900 hover:to-purple-900 text-white border-indigo-500/40 hover:border-indigo-300 hover:shadow-md hover:shadow-indigo-500/20'
                }`}
                title="Launch Agent 72 Strategic Decision Advisor"
              >
                {/* Glowing Aura Ring */}
                <span className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur-xs opacity-40 group-hover:opacity-80 transition duration-300 pointer-events-none" />

                {/* Avatar with Live Beacon */}
                <div className="relative w-7 h-7 rounded-full overflow-hidden bg-white p-0.5 shrink-0 shadow-inner flex items-center justify-center border border-white/30">
                  <img
                    src={agent72Robot}
                    alt="Agent 72 Bot"
                    className="w-full h-full object-contain group-hover:scale-110 transition-transform duration-300"
                  />
                  <span className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-emerald-400 ring-1 ring-white animate-pulse" />
                </div>

                <div className="relative flex flex-col text-left leading-tight">
                  <div className="flex items-center gap-1">
                    <span className="text-[11px] font-black tracking-wide uppercase">Ask Agent 72</span>
                    <Sparkles className="w-3 h-3 text-amber-300 animate-pulse" />
                  </div>
                  <span className="text-[8.5px] text-blue-200 font-medium tracking-tight">AI Strategic Advisor</span>
                </div>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
