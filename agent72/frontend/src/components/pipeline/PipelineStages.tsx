import React from 'react';
import { Target, TrendingUp, Lightbulb, Split, FileCheck } from 'lucide-react';

interface PipelineStagesProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
}

export const PipelineStages: React.FC<PipelineStagesProps> = ({ activeTab, onSelectTab }) => {
  const stages = [
    {
      id: 'position',
      number: '1',
      question: 'WHERE ARE WE?',
      title: 'Current Position',
      subtitle: 'Baseline performance & gaps',
      icon: Target,
      targetTab: 'position',
    },
    {
      id: 'trajectory',
      number: '2',
      question: 'WHERE ARE WE HEADING?',
      title: 'Trajectory',
      subtitle: 'Direction & momentum',
      icon: TrendingUp,
      targetTab: 'trajectory',
    },
    {
      id: 'intelligence',
      number: '3',
      question: 'WHAT MATTERS?',
      title: 'Strategic Intelligence',
      subtitle: 'Risks, constraints & factors',
      icon: Lightbulb,
      targetTab: 'intelligence',
    },
    {
      id: 'options',
      number: '4',
      question: 'WHAT CAN WE DO?',
      title: 'Strategic Options',
      subtitle: 'Choices & 4 scenarios',
      icon: Split,
      targetTab: 'options',
    },
    {
      id: 'plan',
      number: '5',
      question: 'WHAT SHOULD THE PLAN CONTAIN?',
      title: 'Strategic Plan',
      subtitle: 'Targets, initiatives & review',
      icon: FileCheck,
      targetTab: 'plan',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
      {stages.map((st) => {
        const Icon = st.icon;
        const isActive = activeTab === st.targetTab;
        return (
          <button
            key={st.id}
            onClick={() => onSelectTab(st.targetTab)}
            className={`group text-left p-3 rounded-xl border transition-all duration-150 flex flex-col justify-between ${
              isActive
                ? 'bg-blue-600 text-white border-blue-600 shadow-sm shadow-blue-500/20'
                : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200/90 shadow-xs'
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1.5">
              <span
                className={`text-[10px] font-extrabold uppercase tracking-wider ${
                  isActive ? 'text-blue-100' : 'text-blue-600'
                }`}
              >
                {st.question}
              </span>
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-blue-600'}`} />
            </div>
            <div>
              <div className="text-xs font-bold leading-snug">{st.title}</div>
              <div className={`text-[11px] truncate ${isActive ? 'text-blue-100' : 'text-slate-400'}`}>
                {st.subtitle}
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
};
