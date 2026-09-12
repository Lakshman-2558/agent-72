import React from 'react';
import {
  LayoutDashboard,
  Target,
  TrendingUp,
  Lightbulb,
  Split,
  FileCheck,
  CheckSquare,
} from 'lucide-react';

interface WorkspaceTabsProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
}

export const WorkspaceTabs: React.FC<WorkspaceTabsProps> = ({ activeTab, onSelectTab }) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'position', label: 'Current Position', icon: Target },
    { id: 'trajectory', label: 'Trajectory', icon: TrendingUp },
    { id: 'intelligence', label: 'Intelligence', icon: Lightbulb },
    { id: 'options', label: 'Options', icon: Split },
    { id: 'plan', label: 'Strategic Plan', icon: FileCheck },
    { id: 'review', label: 'Review', icon: CheckSquare },
  ];

  return (
    <div className="border-b border-slate-200 pb-2">
      <nav className="flex flex-wrap items-center gap-1.5" aria-label="Tabs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white font-bold shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-100 border border-slate-200/80'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
};
