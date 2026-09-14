import React from 'react';
import { Building2, Calendar, Radio, RotateCcw, Shield } from 'lucide-react';
import { Institution } from '../../api/types';

interface AgentHeaderProps {
  institutions: Institution[];
  selectedInstitutionId: string;
  onSelectInstitution: (id: string) => void;
  selectedPeriod: string;
  onSelectPeriod: (period: string) => void;
  isConnected: boolean;
  onRefresh?: () => void;
}

export const AgentHeader: React.FC<AgentHeaderProps> = ({
  institutions,
  selectedInstitutionId,
  onSelectInstitution,
  selectedPeriod,
  onSelectPeriod,
  isConnected,
  onRefresh,
}) => {
  const periods = ['2024-2025', '2025-2026', '2026-2027', '2023-2024'];

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-[#D7E4EE] shadow-2xs">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Branding */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#163A63] flex items-center justify-center text-white shadow-xs">
            <span className="font-extrabold text-sm tracking-wider">72</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-[#163A63] tracking-tight text-base">Agent 72</span>
              <span className="text-[10.5px] font-bold px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
                DECISION SUPPORT
              </span>
            </div>
            <p className="text-[11px] font-semibold text-[#6B7F91]">
              Strategic Planning Agent
            </p>
          </div>
        </div>

        {/* Right: Institutional Context & Controls */}
        <div className="flex items-center gap-2.5">
          {/* Institution Selector */}
          <div className="relative inline-flex items-center gap-1.5 bg-[#F5F9FC] hover:bg-white border border-[#D7E4EE] rounded-lg px-2.5 py-1.5 text-xs text-[#19324A] transition-colors shadow-2xs">
            <Building2 className="w-3.5 h-3.5 text-[#2F6EA6]" />
            <select
              value={selectedInstitutionId}
              onChange={(e) => onSelectInstitution(e.target.value)}
              className="bg-transparent font-semibold text-[#19324A] focus:outline-none cursor-pointer pr-1"
            >
              {institutions.map((inst) => (
                <option key={inst.id} value={inst.id}>
                  {inst.name} ({inst.code})
                </option>
              ))}
            </select>
          </div>

          {/* Academic Period Selector */}
          <div className="relative inline-flex items-center gap-1.5 bg-[#F5F9FC] hover:bg-white border border-[#D7E4EE] rounded-lg px-2.5 py-1.5 text-xs text-[#19324A] transition-colors shadow-2xs">
            <Calendar className="w-3.5 h-3.5 text-[#2F6EA6]" />
            <select
              value={selectedPeriod}
              onChange={(e) => onSelectPeriod(e.target.value)}
              className="bg-transparent font-semibold text-[#19324A] focus:outline-none cursor-pointer pr-1"
            >
              {periods.map((p) => (
                <option key={p} value={p}>
                  FY {p}
                </option>
              ))}
            </select>
          </div>

          {/* Refresh Action */}
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-1.5 rounded-lg border border-[#D7E4EE] bg-[#F5F9FC] hover:bg-white text-[#6B7F91] hover:text-[#163A63] transition shadow-2xs"
              title="Refresh analytical snapshots"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Live Status Indicator */}
          <div className="flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg border border-[#D7E4EE] bg-[#F5F9FC]">
            <Radio className={`w-3 h-3 ${isConnected ? 'text-[#16805C]' : 'text-[#6B7F91]'}`} />
            <span className={isConnected ? 'text-[#16805C]' : 'text-[#6B7F91]'}>
              {isConnected ? 'API Online' : 'Connecting'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

