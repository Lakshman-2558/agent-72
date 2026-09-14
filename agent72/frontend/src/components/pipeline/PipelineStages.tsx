import React from 'react';
import {
  Database,
  Target,
  TrendingUp,
  Brain,
  Split,
  Layers,
  ListOrdered,
  FileCheck,
  CheckSquare,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
} from 'lucide-react';
import {
  CurrentPositionAnalysis,
  TrajectoryAnalysis,
  StrategicIntelligenceAnalysis,
  StrategicOptionsAnalysis,
  StrategicPlan,
  ExecutionReview,
} from '../../api/types';

interface PipelineStagesProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
  currentPosition?: CurrentPositionAnalysis | null;
  trajectory?: TrajectoryAnalysis | null;
  intelligence?: StrategicIntelligenceAnalysis | null;
  options?: StrategicOptionsAnalysis | null;
  plan?: StrategicPlan | null;
  latestReview?: ExecutionReview | null;
}

type StageStatus = 'available' | 'completed' | 'current' | 'insufficient_evidence';

export const PipelineStages: React.FC<PipelineStagesProps> = ({
  activeTab,
  onSelectTab,
  currentPosition,
  trajectory,
  intelligence,
  options,
  plan,
  latestReview,
}) => {
  // Determine real stage statuses based on actual backend data
  const hasEvidence = Boolean(
    (currentPosition?.key_metrics && currentPosition.key_metrics.length > 0) ||
    (currentPosition?.metric_assessments && currentPosition.metric_assessments.length > 0)
  );

  const getStageState = (tabId: string, hasData: boolean, isCompleted: boolean): StageStatus => {
    if (activeTab === tabId) return 'current';
    if (isCompleted) return 'completed';
    if (hasData) return 'available';
    return 'insufficient_evidence';
  };

  const stages: {
    id: string;
    title: string;
    targetTab: string;
    icon: any;
    status: StageStatus;
  }[] = [
    {
      id: 'evidence',
      title: 'Evidence',
      targetTab: 'overview',
      icon: Database,
      status: getStageState('overview', hasEvidence, hasEvidence),
    },
    {
      id: 'position',
      title: 'Current Position',
      targetTab: 'overview',
      icon: Target,
      status: getStageState('overview', !!currentPosition, !!currentPosition),
    },
    {
      id: 'trajectory',
      title: 'Trajectory',
      targetTab: 'overview',
      icon: TrendingUp,
      status: getStageState('overview', !!trajectory, !!trajectory),
    },
    {
      id: 'intelligence',
      title: 'Strategic Intel',
      targetTab: 'intelligence',
      icon: Brain,
      status: getStageState('intelligence', !!intelligence, !!intelligence),
    },
    {
      id: 'options',
      title: 'Options',
      targetTab: 'options',
      icon: Split,
      status: getStageState('options', !!options?.options?.length, !!options?.options?.length),
    },
    {
      id: 'scenarios',
      title: 'Scenarios',
      targetTab: 'options',
      icon: Layers,
      status: getStageState('options', !!options?.scenarios?.length, !!options?.scenarios?.length),
    },
    {
      id: 'prioritization',
      title: 'Prioritization',
      targetTab: 'options',
      icon: ListOrdered,
      status: getStageState('options', !!options?.evaluations?.length, !!options?.evaluations?.length),
    },
    {
      id: 'plan',
      title: 'Strategic Plan',
      targetTab: 'plan',
      icon: FileCheck,
      status: getStageState('plan', !!plan, plan?.status === 'APPROVED' || plan?.status === 'ACTIVE'),
    },
    {
      id: 'review',
      title: 'Execution Review',
      targetTab: 'review',
      icon: CheckSquare,
      status: getStageState('review', !!latestReview, !!latestReview),
    },
  ];

  const getStatusBadge = (status: StageStatus) => {
    switch (status) {
      case 'current':
        return (
          <span className="text-[9.5px] font-bold px-1.5 py-0.2 rounded bg-white text-[#163A63] border border-[#D7E4EE]">
            Current
          </span>
        );
      case 'completed':
        return (
          <span className="text-[9.5px] font-bold px-1.5 py-0.2 rounded bg-[#E8F4FB] text-[#16805C] border border-[#A7F3D0] flex items-center gap-0.5">
            <CheckCircle2 className="w-2.5 h-2.5" />
            Done
          </span>
        );
      case 'available':
        return (
          <span className="text-[9.5px] font-bold px-1.5 py-0.2 rounded bg-[#E8F4FB] text-[#2F6EA6] border border-[#D7E4EE]">
            Available
          </span>
        );
      case 'insufficient_evidence':
      default:
        return (
          <span className="text-[9.5px] font-medium px-1.5 py-0.2 rounded bg-[#F5F9FC] text-[#6B7F91] border border-[#D7E4EE]">
            No Data
          </span>
        );
    }
  };

  return (
    <div className="bg-white border border-[#D7E4EE] rounded-2xl p-3 shadow-2xs">
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#D7E4EE]">
        <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#163A63]">
          Agent 72 Pipeline
        </span>
        <span className="text-[10px] text-[#6B7F91] font-medium">
          Evidence → Current Position → Trajectory → Intelligence → Options → Scenarios → Prioritization → Plan → Review
        </span>
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-9 gap-1.5">
        {stages.map((st, idx) => {
          const Icon = st.icon;
          const isCurrent = st.status === 'current';

          return (
            <button
              key={st.id}
              onClick={() => onSelectTab(st.targetTab)}
              className={`p-2 rounded-xl border text-left flex flex-col justify-between transition-all ${
                isCurrent
                  ? 'bg-[#163A63] text-white border-[#163A63] shadow-xs'
                  : 'bg-[#F5F9FC] hover:bg-white text-[#19324A] border-[#D7E4EE]'
              }`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <span className="text-[10px] font-bold opacity-75">{idx + 1}</span>
                <Icon className={`w-3.5 h-3.5 ${isCurrent ? 'text-white' : 'text-[#2F6EA6]'}`} />
              </div>
              <div className="text-[11px] font-bold truncate leading-tight my-0.5">
                {st.title}
              </div>
              <div className="mt-1">
                {getStatusBadge(st.status)}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

