import React from 'react';
import {
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  Lightbulb,
  AlertCircle,
  ArrowUpRight,
  Globe,
  Lock,
  Database,
  HelpCircle,
} from 'lucide-react';

export type HighlightCategory =
  | 'STRATEGIC_RISK'
  | 'GAP'
  | 'OPPORTUNITY'
  | 'CONSTRAINT'
  | 'TRAJECTORY_SIGNAL'
  | 'EXECUTION_ALERT'
  | 'EVIDENCE_GAP';

export interface HighlightItem {
  id: string;
  category: HighlightCategory;
  categoryLabel: string;
  title: string;
  description: string;
  primaryValue?: string;
  comparisonValue?: string;
  badge?: string;
  semanticStatus: 'green' | 'amber' | 'red' | 'blue';
  targetTab: string;
}

interface HighlightCardProps {
  item: HighlightItem;
  onClick: () => void;
}

export const HighlightCard: React.FC<HighlightCardProps> = ({ item, onClick }) => {
  const getIcon = () => {
    switch (item.category) {
      case 'STRATEGIC_RISK':
        return <AlertTriangle className="w-3.5 h-3.5 text-[#C44B55]" />;
      case 'GAP':
        return <AlertCircle className="w-3.5 h-3.5 text-[#C44B55]" />;
      case 'OPPORTUNITY':
        return <Lightbulb className="w-3.5 h-3.5 text-[#16805C]" />;
      case 'CONSTRAINT':
        return <Lock className="w-3.5 h-3.5 text-[#B7791F]" />;
      case 'TRAJECTORY_SIGNAL':
        return <TrendingUp className="w-3.5 h-3.5 text-[#2F6EA6]" />;
      case 'EXECUTION_ALERT':
        return <AlertCircle className="w-3.5 h-3.5 text-[#B7791F]" />;
      case 'EVIDENCE_GAP':
        return <Database className="w-3.5 h-3.5 text-[#6B7F91]" />;
      default:
        return <HelpCircle className="w-3.5 h-3.5 text-[#2F6EA6]" />;
    }
  };

  const getBorderColor = () => {
    switch (item.semanticStatus) {
      case 'red':
        return 'border-l-4 border-l-[#C44B55]';
      case 'amber':
        return 'border-l-4 border-l-[#B7791F]';
      case 'green':
        return 'border-l-4 border-l-[#16805C]';
      case 'blue':
      default:
        return 'border-l-4 border-l-[#2F6EA6]';
    }
  };

  const getBadgeStyle = () => {
    switch (item.semanticStatus) {
      case 'red':
        return 'bg-[#FEE2E2] text-[#C44B55] border-[#FECACA]';
      case 'amber':
        return 'bg-[#FEF9C3] text-[#B7791F] border-[#FDE68A]';
      case 'green':
        return 'bg-[#E8F4FB] text-[#16805C] border-[#A7F3D0]';
      case 'blue':
      default:
        return 'bg-[#E8F4FB] text-[#163A63] border-[#D7E4EE]';
    }
  };

  return (
    <div
      onClick={onClick}
      className={`p-3.5 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs hover:shadow-xs transition-all cursor-pointer ${getBorderColor()}`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-1.5">
          {getIcon()}
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-[#6B7F91]">
            {item.categoryLabel}
          </span>
        </div>
        <ArrowUpRight className="w-3.5 h-3.5 text-[#6B7F91] hover:text-[#163A63] transition-colors" />
      </div>

      <h4 className="text-xs font-bold text-[#19324A] leading-snug">{item.title}</h4>
      <p className="text-[11px] text-[#6B7F91] mt-1 leading-relaxed line-clamp-2">{item.description}</p>

      {(item.primaryValue || item.badge) && (
        <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-[#D7E4EE] text-xs">
          {item.primaryValue && (
            <div className="flex items-baseline gap-1.5">
              <span className="font-bold text-[#19324A] text-xs">{item.primaryValue}</span>
              {item.comparisonValue && (
                <span className="text-[10.5px] text-[#6B7F91]">target: {item.comparisonValue}</span>
              )}
            </div>
          )}
          {item.badge && (
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getBadgeStyle()}`}>
              {item.badge}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

