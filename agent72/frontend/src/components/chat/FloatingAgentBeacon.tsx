import React, { useState } from 'react';
import { Sparkles, ArrowRight, MessageSquareQuote } from 'lucide-react';
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
      className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-40 flex flex-col items-end gap-2 pointer-events-auto select-none"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Floating Prompt Preview Card on Hover */}
      {isHovered && (
        <div className="bg-slate-900/95 backdrop-blur-md text-white px-4 py-3 rounded-2xl shadow-2xl border border-indigo-500/50 text-xs max-w-xs animate-in fade-in slide-in-from-bottom-2 duration-200 z-30 mb-1">
          <div className="flex items-center gap-1.5 text-amber-300 font-bold text-[11px] mb-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Agent 72 Strategic Advisor</span>
          </div>
          <p className="text-slate-300 text-[11px] leading-relaxed">
            Instant insights on CSE placements, faculty PhD roadmap, and regulatory safety scans.
          </p>
          <div className="mt-2 flex items-center justify-between text-[10px] text-blue-300 font-semibold pt-1.5 border-t border-slate-700/60">
            <span>Click to launch advisor</span>
            <ArrowRight className="w-3 h-3" />
          </div>
        </div>
      )}

      {/* Container holding peek-a-boo bot and main button */}
      <div className="relative">
        {/* Hide-and-Seek Peek-a-boo Bot popping up and down from back side of button */}
        <div
          className={`absolute -top-16 sm:-top-20 right-5 sm:right-6 z-10 pointer-events-none transition-all duration-500 ease-out flex flex-col items-center ${
            isHovered
              ? 'translate-y-[-28px] scale-115 opacity-100'
              : 'animate-peek-a-boo'
          }`}
        >
          {/* Playful mini speech badge when peaking */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-[10px] font-bold px-2.5 py-0.5 rounded-full shadow-lg border border-indigo-300/40 whitespace-nowrap mb-1 flex items-center gap-1 drop-shadow-md">
            <Sparkles className="w-3 h-3 text-amber-300 animate-pulse" />
            <span>I'm here! 👋</span>
          </div>

          {/* Peek-a-boo Bot Head with playful tilt (Enlarged) */}
          <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-white p-1.5 shadow-2xl border-2 border-indigo-500/80 overflow-hidden animate-bot-wiggle ring-4 ring-indigo-300/40">
            <img
              src={agent72Robot}
              alt="Peek-a-boo Agent 72 Bot"
              className="w-full h-full object-contain"
            />
          </div>
        </div>

        {/* Main Glowing AI Button (z-20 so it sits in front of the peeking bot) */}
        <button
          onClick={onOpenAskAgent}
          className="relative z-20 group flex items-center gap-3 bg-gradient-to-r from-[#163A63] via-[#1E4E79] to-[#2B6CB0] hover:from-blue-600 hover:via-indigo-600 hover:to-purple-600 text-white pl-2.5 pr-5 py-2.5 rounded-full shadow-xl shadow-blue-900/30 hover:shadow-indigo-500/35 border border-indigo-400/50 hover:border-indigo-300 transition-all duration-300 transform hover:scale-105 active:scale-95 cursor-pointer"
        >
          {/* Iridescent Outer Pulse Aura */}
          <span className="absolute -inset-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 rounded-full blur-sm opacity-50 group-hover:opacity-90 animate-pulse transition duration-500 pointer-events-none" />

          {/* Shimmer overlay */}
          <span className="absolute top-0 -left-[100%] w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent group-hover:left-[100%] transition-all duration-1000 ease-in-out pointer-events-none rounded-full" />

          {/* Robot Avatar Orb (Enlarged) */}
          <div className="relative w-13 h-13 sm:w-14 sm:h-14 rounded-full bg-white p-1 shadow-inner shrink-0 flex items-center justify-center border border-white/30 group-hover:rotate-6 transition-transform">
            <img
              src={agent72Robot}
              alt="Agent 72 Robot"
              className="w-full h-full object-contain"
            />
            {/* Live Beacon */}
            <span className="absolute -bottom-0.5 -right-0.5 flex h-3.5 w-3.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-white" />
            </span>
          </div>

          {/* Label & Sparks */}
          <div className="relative flex flex-col text-left">
            <div className="flex items-center gap-1.5">
              <span className="text-xs sm:text-sm font-black tracking-wide uppercase text-white drop-shadow-xs">
                Ask Agent 72
              </span>
              <span className="px-1.5 py-0.2 text-[8.5px] font-black uppercase rounded-full bg-indigo-400/30 text-indigo-100 border border-indigo-300/40">
                AI
              </span>
            </div>
            <span className="text-[10px] text-blue-200 font-semibold flex items-center gap-1">
              <span>Strategic Decision Advisor</span>
            </span>
          </div>
        </button>
      </div>
    </aside>
  );
};

