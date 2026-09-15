import React from 'react';
import {
  LayoutDashboard,
  Brain,
  Split,
  FileCheck,
  CheckSquare,
  MessageSquareQuote,
  Sparkles,
} from 'lucide-react';

interface WorkspaceTabsProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
}

export const WorkspaceTabs: React.FC<WorkspaceTabsProps> = ({ activeTab, onSelectTab }) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'intelligence', label: 'Strategic Intelligence', icon: Brain },
    { id: 'options', label: 'Options & Scenarios', icon: Split },
    { id: 'plan', label: 'Strategic Plan', icon: FileCheck },
    { id: 'review', label: 'Execution Review', icon: CheckSquare },
    { id: 'ask', label: 'Ask Agent 72', icon: Sparkles, isAi: true },
  ];

  return (
    <div className="border-b border-[#D7E4EE] pb-1">
      <nav className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-1 scroll-smooth" aria-label="Workspace Tabs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          if (tab.isAi) {
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`relative group shrink-0 ml-auto sm:ml-2 flex items-center gap-2 px-4 py-2 text-xs font-black rounded-xl transition-all duration-300 overflow-hidden cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-[#163A63] via-indigo-700 to-purple-800 text-white shadow-md shadow-indigo-500/25 border border-indigo-400 ring-2 ring-indigo-300/40'
                    : 'bg-gradient-to-r from-slate-900 via-indigo-950 to-[#163A63] hover:from-blue-900 hover:via-indigo-900 hover:to-purple-900 text-white border border-indigo-400/40 shadow-xs hover:shadow-md hover:shadow-indigo-500/20'
                }`}
              >
                {/* Shimmer Light Beam Effect */}
                <span className="absolute top-0 -left-[100%] w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent group-hover:left-[100%] transition-all duration-700 ease-in-out pointer-events-none" />

                {/* Live Pulse Dot */}
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>

                <Icon className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
                <span className="tracking-wide">{tab.label}</span>

                <span className="text-[8.5px] font-black uppercase px-1.5 py-0.2 rounded-full bg-white/20 text-indigo-100 border border-white/10 tracking-wider">
                  AI
                </span>
              </button>
            );
          }

          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-xl transition-colors shrink-0 cursor-pointer ${
                isActive
                  ? 'bg-[#163A63] text-white shadow-2xs border border-[#163A63]'
                  : 'text-[#19324A] hover:text-[#163A63] bg-white hover:bg-[#E8F4FB] border border-[#D7E4EE]'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-[#2F6EA6]'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
};

