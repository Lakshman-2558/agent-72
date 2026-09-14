import React from 'react';
import { ShieldCheck, ArrowRight } from 'lucide-react';
import agent72Robot from '../../assets/agent72-robot.png';

export const AgentHero: React.FC = () => {
  return (
    <div className="bg-[#E8F4FB] border border-[#D7E4EE] rounded-2xl p-4 sm:p-5 shadow-2xs">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-1.5 max-w-3xl">
          <div className="flex items-center gap-3">
            {/* Agent 72 AI Bot Image */}
            <div className="w-12 h-12 rounded-xl overflow-hidden border border-[#D7E4EE] bg-white p-1 shadow-xs shrink-0 flex items-center justify-center">
              <img
                src={agent72Robot}
                alt="Agent 72"
                className="w-full h-full object-contain"
              />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-extrabold text-[#163A63] tracking-tight">
                  Agent 72
                </h1>
                <span className="text-xs font-bold text-[#2F6EA6] px-2 py-0.5 rounded bg-white border border-[#D7E4EE]">
                  Strategic Planning Agent
                </span>
              </div>
              <div className="text-[11px] sm:text-xs font-bold text-[#2F6EA6] flex items-center gap-1.5 mt-0.5">
                <span>Evidence</span>
                <ArrowRight className="w-3 h-3 text-[#163A63]" />
                <span>Intelligence</span>
                <ArrowRight className="w-3 h-3 text-[#163A63]" />
                <span>Strategic Action</span>
              </div>
            </div>
          </div>

          <p className="text-xs text-[#19324A] leading-relaxed pt-1">
            Agent 72 converts institutional evidence into strategic intelligence, evaluated options, and measurable planning artifacts for leadership decision support. Final strategic choices, resource allocation, and governance remain with institutional leadership.
          </p>
        </div>

        <div className="hidden md:flex flex-col items-end shrink-0 text-right space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#163A63]">
            <ShieldCheck className="w-4 h-4 text-[#16805C]" />
            <span>Deterministic Analysis</span>
          </div>
          <p className="text-[11px] text-[#6B7F91]">
            Evidence-grounded decision support
          </p>
        </div>
      </div>
    </div>
  );
};
