import React, { useState } from 'react';
import { Sparkles, MessageSquareQuote, ArrowRight, Bot } from 'lucide-react';
import agent72Robot from '../../assets/agent72-robot.png';

interface FloatingAgentBeaconProps {
  activeTab: string;
  onOpenAskAgent: () => void;
}

export const FloatingAgentBeacon: React.FC<FloatingAgentBeaconProps> = ({
  activeTab,
  onOpenAskAgent,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  // If already in the ask tab, hide or show minimal state
  if (activeTab === 'ask') return null;

  return (
    <aside
      aria-label="Agent 72 Quick Launcher"
      className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-2 pointer-events-auto select-none"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Floating Prompt Preview Card on Hover */}
      {isHovered && (
        <div className="bg-slate-900/95 backdrop-blur-md text-white px-4 py-2.5 rounded-2xl shadow-xl border border-indigo-500/40 text-xs max-w-xs animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center gap-1.5 text-amber-300 font-bold text-[11px] mb-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Agent 72 Strategic Decision Advisor</span>
          </div>
          <p className="text-slate-300 text-[11px] leading-relaxed">
            Instant insights on CSE placements, faculty PhD roadmap, and regulatory safety scans.
          </p>
          <div className="mt-2 flex items-center justify-between text-[10px] text-blue-300 font-semibold pt-1.5 border-t border-slate-700/60">
            <span>Click to launch conversation</span>
            <ArrowRight className="w-3 h-3" />
          </div>
        </div>
      )}

      {/* Main Innovative Glowing AI Button */}
      <button
        onClick={onOpenAskAgent}
        className="relative group flex items-center gap-3 bg-gradient-to-r from-[#163A63] via-[#1E4E79] to-[#2B6CB0] hover:from-blue-600 hover:via-indigo-600 hover:to-purple-600 text-white pl-2 pr-4 py-2 rounded-full shadow-lg shadow-blue-900/30 hover:shadow-indigo-500/35 border border-indigo-400/40 hover:border-indigo-300 transition-all duration-300 transform hover:scale-105 active:scale-95"
      >
        {/* Iridescent Outer Pulse Aura */}
        <span className="absolute -inset-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 rounded-full blur-sm opacity-50 group-hover:opacity-90 animate-pulse transition duration-500 pointer-events-none" />

        {/* Shimmer overlay */}
        <span className="absolute top-0 -left-[100%] w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent group-hover:left-[100%] transition-all duration-1000 ease-in-out pointer-events-none rounded-full" />

        {/* Robot Avatar Orb */}
        <div className="relative w-10 h-10 rounded-full bg-white p-1 shadow-inner shrink-0 flex items-center justify-center border border-white/30 group-hover:rotate-6 transition-transform">
          <img
            src={agent72Robot}
            alt="Agent 72 Robot"
            className="w-full h-full object-contain"
          />
          {/* Live Beacon */}
          <span className="absolute -bottom-0.5 -right-0.5 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border-2 border-white" />
          </span>
        </div>

        {/* Label & Sparks */}
        <div className="relative flex flex-col text-left">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-black tracking-wide uppercase text-white drop-shadow-xs">
              Ask Agent 72
            </span>
            <span className="px-1.5 py-0.2 text-[8px] font-black uppercase rounded-full bg-indigo-400/30 text-indigo-100 border border-indigo-300/40">
              AI
            </span>
          </div>
          <span className="text-[9.5px] text-blue-200 font-semibold flex items-center gap-1">
            <span>Online Decision Support</span>
          </span>
        </div>
      </button>
    </aside>
  );
};
