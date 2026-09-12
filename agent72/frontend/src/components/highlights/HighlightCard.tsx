import React from 'react';
import { AlertTriangle, TrendingDown, Lightbulb, AlertCircle, ArrowUpRight, Globe } from 'lucide-react';

export interface HighlightItem {
  id: string;
  category: 'HIGH_PRIORITY' | 'OPPORTUNITY' | 'TRAJECTORY_SHIFT' | 'EXECUTION_ALERT' | 'TARGET_AT_RISK' | 'EXTERNAL_SIGNAL';
  categoryLabel: string;
  title: string;
  description: string;
  primaryValue?: string;
  comparisonValue?: string;
  badge?: string;
  badgeType?: 'danger' | 'warning' | 'success' | 'info';
  targetTab: string;
}

interface HighlightCardProps {
  item: HighlightItem;
  onClick: () => void;
}

export const HighlightCard: React.FC<HighlightCardProps> = ({ item, onClick }) => {
  const getIcon = () => {
    switch (item.category) {
      case 'HIGH_PRIORITY':
        return <AlertTriangle className="w-4 h-4 text-rose-600" />;
      case 'OPPORTUNITY':
        return <Lightbulb className="w-4 h-4 text-amber-600" />;
      case 'TRAJECTORY_SHIFT':
        return <TrendingDown className="w-4 h-4 text-rose-600" />;
      case 'EXECUTION_ALERT':
      case 'TARGET_AT_RISK':
        return <AlertCircle className="w-4 h-4 text-amber-600" />;
      case 'EXTERNAL_SIGNAL':
        return <Globe className="w-4 h-4 text-blue-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-blue-600" />;
    }
  };

  const getBorderColor = () => {
    switch (item.category) {
      case 'HIGH_PRIORITY':
      case 'TRAJECTORY_SHIFT':
        return 'border-l-4 border-l-rose-500 hover:border-slate-300';
      case 'OPPORTUNITY':
        return 'border-l-4 border-l-amber-500 hover:border-slate-300';
      case 'EXECUTION_ALERT':
      case 'TARGET_AT_RISK':
        return 'border-l-4 border-l-amber-500 hover:border-slate-300';
      case 'EXTERNAL_SIGNAL':
        return 'border-l-4 border-l-blue-500 hover:border-slate-300';
      default:
        return 'border-l-4 border-l-slate-400 hover:border-slate-300';
    }
  };

  return (
    <div
      onClick={onClick}
      className={`p-3.5 bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-all cursor-pointer ${getBorderColor()}`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-1.5">
          {getIcon()}
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500">
            {item.categoryLabel}
          </span>
        </div>
        <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 hover:text-blue-600 transition-colors" />
      </div>

      <h4 className="text-xs font-bold text-slate-900 leading-snug">{item.title}</h4>
      <p className="text-[11px] text-slate-600 mt-1 leading-relaxed line-clamp-2">{item.description}</p>

      {(item.primaryValue || item.badge) && (
        <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-slate-100 text-xs">
          {item.primaryValue && (
            <div className="flex items-baseline gap-1.5">
              <span className="font-bold text-slate-900">{item.primaryValue}</span>
              {item.comparisonValue && (
                <span className="text-[11px] text-slate-400">target: {item.comparisonValue}</span>
              )}
            </div>
          )}
          {item.badge && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
              {item.badge}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
