import React from 'react';
import { Bell, Sparkles } from 'lucide-react';
import { HighlightCard, HighlightItem } from './HighlightCard';
import {
  CurrentPositionAnalysis,
  TrajectoryAnalysis,
  StrategicIntelligenceAnalysis,
  StrategicOptionsAnalysis,
  StrategicPlan,
  ExecutionReview,
} from '../../api/types';

interface HighlightsPanelProps {
  currentPosition?: CurrentPositionAnalysis | null;
  trajectory?: TrajectoryAnalysis | null;
  intelligence?: StrategicIntelligenceAnalysis | null;
  options?: StrategicOptionsAnalysis | null;
  activePlan?: StrategicPlan | null;
  latestReview?: ExecutionReview | null;
  onNavigateTab: (tab: string) => void;
}

export const HighlightsPanel: React.FC<HighlightsPanelProps> = ({
  currentPosition,
  trajectory,
  intelligence,
  options,
  activePlan,
  latestReview,
  onNavigateTab,
}) => {
  const highlights: HighlightItem[] = [];

  // 1. High Priority Alert: Critical Gap or High Severity Risk
  if (currentPosition?.metric_assessments) {
    const criticalGap = currentPosition.metric_assessments.find(
      (m) => (m.gap !== null && m.gap !== undefined && m.gap < -5) || m.performance_band === 'DEFICIT'
    );
    if (criticalGap) {
      const gapNotation = criticalGap.gap !== null && criticalGap.gap !== undefined
        ? `${criticalGap.gap > 0 ? '+' : ''}${criticalGap.gap.toFixed(1)} ${criticalGap.gap_unit_label || criticalGap.unit || 'percentage points'}`
        : 'Negative gap noted';
      highlights.push({
        id: 'hl-high-priority',
        category: 'HIGH_PRIORITY',
        categoryLabel: 'HIGH PRIORITY',
        title: `${criticalGap.metric_name || criticalGap.metric_key} Performance`,
        description: `Current observation shows an acute gap of ${gapNotation} against institutional target.`,
        primaryValue: criticalGap.observed_value !== null ? `${criticalGap.observed_value} ${criticalGap.unit || ''}` : 'Insufficient evidence',
        comparisonValue: criticalGap.target_value !== null ? `${criticalGap.target_value} ${criticalGap.unit || ''}` : undefined,
        badge: 'Gap Warning',
        targetTab: 'position',
      });
    }
  }

  // 2. Trajectory Shift: Declining metric
  if (trajectory?.metric_trajectories) {
    const declining = trajectory.metric_trajectories.find((t) => t.status === 'DECLINING');
    if (declining) {
      highlights.push({
        id: 'hl-trajectory-shift',
        category: 'TRAJECTORY_SHIFT',
        categoryLabel: 'TRAJECTORY SHIFT',
        title: `${declining.metric_name || declining.metric_key} Momentum`,
        description: `Longitudinal analysis indicates downward movement over ${declining.observation_count} historical periods.`,
        primaryValue: declining.net_change !== null && declining.net_change !== undefined ? `${declining.net_change > 0 ? '+' : ''}${declining.net_change.toFixed(1)} ${declining.unit || ''}` : undefined,
        badge: 'Declining',
        targetTab: 'trajectory',
      });
    }
  }


  // 3. Strategic Opportunity
  if (intelligence?.opportunities && intelligence.opportunities.length > 0) {
    const topOpp = intelligence.opportunities[0];
    highlights.push({
      id: 'hl-opportunity',
      category: 'OPPORTUNITY',
      categoryLabel: 'STRATEGIC OPPORTUNITY',
      title: topOpp.title,
      description: topOpp.description || 'Institutional capacity and evidence demonstrate strong upside potential.',
      badge: `${Math.round((topOpp.confidence || 0.8) * 100)}% Confidence`,
      targetTab: 'intelligence',
    });
  }

  // 4. Execution Review Alert
  if (latestReview) {
    const offTrack = latestReview.metric_variances?.find((v) => v.status === 'OFF_TRACK' || v.status === 'AT_RISK');
    if (offTrack) {
      highlights.push({
        id: 'hl-execution-alert',
        category: 'EXECUTION_ALERT',
        categoryLabel: 'EXECUTION ALERT',
        title: `Target Alert: ${offTrack.metric_key}`,
        description: `Variance observed: ${offTrack.variance_notation}. Operational intervention recommended.`,
        badge: offTrack.status,
        targetTab: 'review',
      });
    }
  }

  // 5. External Environment Signal
  if (intelligence?.external_factors && intelligence.external_factors.length > 0) {
    const topExt = intelligence.external_factors[0];
    highlights.push({
      id: 'hl-external-signal',
      category: 'EXTERNAL_SIGNAL',
      categoryLabel: 'EXTERNAL FACTOR',
      title: topExt.title,
      description: topExt.description || 'Regional and market forces requiring proactive institutional consideration.',
      badge: topExt.category,
      targetTab: 'intelligence',
    });
  }

  // 6. Priority Strategic Option
  if (options?.options && options.options.length > 0) {
    const topOpt = options.options[0];
    const scoreBadge =
      typeof topOpt.total_score === 'number' ? `Score: ${topOpt.total_score.toFixed(0)}` : 'Evaluated';
    highlights.push({
      id: 'hl-priority-option',
      category: 'HIGH_PRIORITY',
      categoryLabel: 'PRIORITY OPTION',
      title: topOpt.title,
      description: topOpt.strategic_rationale || 'High strategic alignment evaluated for leadership consideration.',
      badge: scoreBadge,
      targetTab: 'options',
    });
  }

  return (
    <div className="bg-slate-50/70 border border-slate-200/90 rounded-2xl p-4 flex flex-col h-full">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-100/80 text-blue-700 rounded-lg">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-800">
              HIGHLIGHTS
            </h3>
            <p className="text-[10px] text-slate-500 font-medium">Real-time leadership alerts</p>
          </div>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
          {highlights.length} Active
        </span>
      </div>

      {/* Independently Scrollable Container */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[calc(100vh-14rem)]">
        {highlights.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-500 italic bg-white rounded-xl border border-slate-200">
            <Sparkles className="w-5 h-5 mx-auto text-slate-400 mb-2" />
            No major highlights from available evidence.
          </div>
        ) : (
          highlights.map((item) => (
            <HighlightCard
              key={item.id}
              item={item}
              onClick={() => onNavigateTab(item.targetTab)}
            />
          ))
        )}
      </div>
    </div>
  );
};
