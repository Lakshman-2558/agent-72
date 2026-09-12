import React from 'react';
import { Compass, Sparkles } from 'lucide-react';

export const AgentHero: React.FC = () => {
  return (
    <div className="relative overflow-hidden bg-gradient-to-r from-blue-500/10 via-sky-500/5 to-white border border-blue-200/70 rounded-2xl p-6 sm:p-7 shadow-xs">
      {/* Background Decorative Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0284c70a_1px,transparent_1px),linear-gradient(to_bottom,#0284c70a_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />

      <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Left: Text Details */}
        <div className="max-w-xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/90 border border-blue-200 text-blue-800 text-xs font-semibold rounded-full shadow-xs backdrop-blur">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>Institutional Leadership Decision Support</span>
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Hello! I'm <span className="text-blue-600">Agent 72</span>
            </h1>
            <p className="text-sm font-semibold text-slate-600 mt-0.5">
              Strategic Planning Agent
            </p>
          </div>

          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            I'm Agent 72, an AI-powered strategic planning agent designed to help institutional
            leadership understand performance, identify strategic issues, evaluate strategic
            choices, and develop evidence-grounded plans.
          </p>

          <div className="pt-1 flex items-center gap-2 text-xs text-slate-500 font-medium">
            <Compass className="w-4 h-4 text-blue-600" />
            <span>Deterministic evidence calculations • AI narrative synthesis • Leadership governance</span>
          </div>
        </div>

        {/* Right: Agent 72 Robot Standing Avatar */}
        <div className="shrink-0 w-40 h-40 sm:w-48 sm:h-44 relative flex items-center justify-center select-none">
          <div className="absolute w-36 h-36 bg-blue-400/25 rounded-full blur-xl pointer-events-none" />
          <img
            src="/agent72-robot.png"
            alt="Agent 72 Avatar"
            className="w-36 h-36 sm:w-40 sm:h-40 object-contain relative z-10 animate-float drop-shadow-md transition-transform duration-300 hover:scale-105"
          />
        </div>
      </div>
    </div>
  );
};
