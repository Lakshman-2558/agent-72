import React from 'react';
import { Institution } from '../../api/types';
import { Settings, Layers } from 'lucide-react';

interface VignanHeaderProps {
  institutions: Institution[];
  selectedInstitutionId: string;
  onSelectInstitution: (id: string) => void;
  selectedPeriod: string;
  onSelectPeriod: (period: string) => void;
  onToggleStrategicView?: () => void;
  isStrategicView?: boolean;
}

export const VignanHeader: React.FC<VignanHeaderProps> = ({
  institutions,
  selectedInstitutionId,
  onSelectInstitution,
  selectedPeriod,
  onSelectPeriod,
  onToggleStrategicView,
  isStrategicView,
}) => {
  return (
    <header className="bg-white border-b border-slate-200/80 px-4 sm:px-6 py-2.5 shadow-xs sticky top-0 z-30">
      <div className="max-w-[1500px] mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Left: Vignan's University Logo & Accreditation Badge */}
        <div className="flex items-center gap-2.5 select-none">
          <div className="flex items-center gap-2">
            {/* Official Vignan University Crest & Identity */}
            <img
              src="/vignan_logo.png"
              alt="Vignan's Foundation for Science, Technology & Research"
              className="h-12 sm:h-14 w-auto object-contain cursor-pointer transition-transform hover:scale-105"
            />
          </div>

          {/* NAAC A+ / NIRF 70 Accreditation Box */}
          <div className="border border-slate-300 rounded px-1.5 py-0.5 text-[8.5px] leading-tight text-center bg-slate-50 font-bold ml-1">
            <div className="text-red-700 font-extrabold text-[9px]">NAAC <span className="text-blue-900">A+</span></div>
            <div className="text-slate-600 text-[7px] border-t border-slate-200 mt-0.5 pt-0.5">
              NIRF <span className="text-red-700 font-black">70<sup className="text-[5px]">th</sup></span>
            </div>
          </div>
        </div>

        {/* Center: CSE PRESENTS / AGENTIC AI DAY 2026 */}
        <div className="text-center select-none">
          <div className="text-[10px] font-bold tracking-widest text-slate-500 uppercase">
            CSE PRESENTS
          </div>
          <h1 className="text-xl sm:text-2xl font-black tracking-wide text-[#1e3a8a] uppercase flex items-center justify-center gap-2">
            <span>AGENTIC AI DAY 2026</span>
          </h1>
        </div>

        {/* Right: Circular Accreditations & Controls */}
        <div className="flex items-center gap-2">
          {/* Circular Badges (NAAC A+, NIRF, NBA, ISO, UGC, ABET) */}
          <div className="hidden lg:flex items-center gap-1.5 select-none mr-2">
            {/* NAAC A+ */}
            <div className="w-7 h-7 rounded-full border border-red-300 bg-red-50/50 flex flex-col items-center justify-center text-[7px] font-black text-red-700 leading-none shadow-2xs" title="NAAC Grade A+">
              <span>NAAC</span>
              <span className="text-red-800 text-[6.5px]">A+</span>
            </div>
            {/* NIRF */}
            <div className="w-7 h-7 rounded-full border border-blue-300 bg-blue-50/50 flex flex-col items-center justify-center text-[6.5px] font-black text-blue-900 leading-none shadow-2xs" title="NIRF Ranked">
              <span>nirf</span>
              <span className="text-[5.5px] text-slate-500">2024</span>
            </div>
            {/* NBA */}
            <div className="w-7 h-7 rounded-full border border-amber-300 bg-amber-50/50 flex flex-col items-center justify-center text-[7px] font-black text-amber-800 leading-none shadow-2xs" title="NBA Accredited">
              <span>NBA</span>
            </div>
            {/* ISO */}
            <div className="w-7 h-7 rounded-full border border-emerald-300 bg-emerald-50/50 flex flex-col items-center justify-center text-[6.5px] font-black text-emerald-800 leading-none shadow-2xs" title="ISO 9001:2015">
              <span>ISO</span>
              <span className="text-[5px] text-emerald-600">9001</span>
            </div>
            {/* UGC */}
            <div className="w-7 h-7 rounded-full border border-purple-300 bg-purple-50/50 flex flex-col items-center justify-center text-[7px] font-black text-purple-800 leading-none shadow-2xs" title="UGC Recognized">
              <span>UGC</span>
            </div>
            {/* ABET */}
            <div className="w-7 h-7 rounded-full border border-sky-300 bg-sky-50/50 flex flex-col items-center justify-center text-[6.5px] font-black text-sky-800 leading-none shadow-2xs" title="ABET Substantial Equivalency">
              <span>ABET</span>
            </div>
          </div>

          {/* Strategic Planning System Switch Button */}
          {onToggleStrategicView && (
            <button
              onClick={onToggleStrategicView}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold transition ${
                isStrategicView
                  ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                  : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
              }`}
              title="Toggle Strategic Governance Workspace"
            >
              <Layers className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">
                {isStrategicView ? 'Assistant View' : 'Strategic System'}
              </span>
            </button>
          )}

          {/* Period Selector */}
          <div className="relative">
            <select
              value={selectedPeriod}
              onChange={(e) => onSelectPeriod(e.target.value)}
              className="bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg px-2 py-1 text-xs font-medium text-slate-700 focus:outline-none cursor-pointer pr-4"
            >
              <option value="2024-2025">2024-2025</option>
              <option value="2026-2027">2026-2027</option>
              <option value="2023-2024">2023-2024</option>
            </select>
          </div>
        </div>
      </div>
    </header>
  );
};
