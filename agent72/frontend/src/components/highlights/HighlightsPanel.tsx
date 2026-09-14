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

  // 1. Gaps (Phase 4: Current Position acute deficits)
  const metrics = currentPosition?.key_metrics || currentPosition?.metric_assessments || [];
  const acuteGap = metrics.find(
    (m: any) =>
      (m.gap !== null && m.gap !== undefined && m.gap < 0) ||
      m.performance_status === 'DEFICIT' ||
      m.performance_band === 'DEFICIT'
  );
  if (acuteGap) {
    const isPct = acuteGap.unit === '%' || acuteGap.unit === 'percent';
    const unitLabel = isPct ? 'percentage points' : acuteGap.unit || '';
    const gapVal = acuteGap.gap !== null && acuteGap.gap !== undefined ? acuteGap.gap.toFixed(1) : 'Below target';
    highlights.push({
      id: 'hl-gap',
      category: 'GAP',
      categoryLabel: 'PERFORMANCE GAP',
      title: `${acuteGap.metric_name || acuteGap.metric_key} Gap`,
      description: `Observed performance reflects a gap of ${gapVal} ${unitLabel} against the baseline target.`,
      primaryValue: acuteGap.observed_value !== null && acuteGap.observed_value !== undefined ? `${acuteGap.observed_value} ${acuteGap.unit || ''}` : 'Insufficient evidence',
      comparisonValue: acuteGap.target_value !== null && acuteGap.target_value !== undefined ? `${acuteGap.target_value} ${acuteGap.unit || ''}` : undefined,
      badge: 'Acute Gap',
      semanticStatus: 'red',
      targetTab: 'overview',
    });
  }

  // 2. Strategic Risks (Phase 6: Risks)
  const risks = intelligence?.risk_signals || intelligence?.risks || [];
  if (risks.length > 0) {
    const topRisk = risks.find((r: any) => r.severity === 'CRITICAL' || r.severity === 'HIGH') || risks[0];
    highlights.push({
      id: 'hl-risk',
      category: 'STRATEGIC_RISK',
      categoryLabel: 'STRATEGIC RISK',
      title: topRisk.title,
      description: topRisk.description || 'Structural cross-metric risk identified from multi-domain evidence.',
      badge: `Severity: ${topRisk.severity}`,
      semanticStatus: topRisk.severity === 'CRITICAL' || topRisk.severity === 'HIGH' ? 'red' : 'amber',
      targetTab: 'intelligence',
    });
  }

  // 3. Trajectory Signals (Phase 5: Trajectory trends)
  const trajectories = trajectory?.metric_trends || trajectory?.metric_trajectories || [];
  const notableTraj =
    trajectories.find((t: any) => t.status === 'DECLINING' || t.status === 'IMPROVING' || t.status === 'VOLATILE') ||
    trajectories[0];
  if (notableTraj) {
    const isDeclining = notableTraj.status === 'DECLINING';
    const isImproving = notableTraj.status === 'IMPROVING';
    highlights.push({
      id: 'hl-trajectory',
      category: 'TRAJECTORY_SIGNAL',
      categoryLabel: 'TRAJECTORY SIGNAL',
      title: `${notableTraj.metric_name || notableTraj.metric_key} Trajectory`,
      description: `Longitudinal analysis indicates ${notableTraj.status.toLowerCase()} directional movement over ${notableTraj.observation_count || 'historical'} periods.`,
      primaryValue:
        notableTraj.net_change !== null && notableTraj.net_change !== undefined
          ? `${notableTraj.net_change > 0 ? '+' : ''}${notableTraj.net_change.toFixed(1)} ${notableTraj.unit || ''}`
          : undefined,
      badge: notableTraj.status.replace(/_/g, ' '),
      semanticStatus: isDeclining ? 'red' : isImproving ? 'green' : 'blue',
      targetTab: 'overview',
    });
  }

  // 4. Strategic Opportunities (Phase 6)
  const opps = intelligence?.opportunity_signals || intelligence?.opportunities || [];
  if (opps.length > 0) {
    const topOpp = opps[0];
    highlights.push({
      id: 'hl-opportunity',
      category: 'OPPORTUNITY',
      categoryLabel: 'OPPORTUNITY',
      title: topOpp.title,
      description: topOpp.description || 'Institutional capacity demonstrates upside strategic potential.',
      badge: `${Math.round((topOpp.confidence || 0.8) * 100)}% Confidence`,
      semanticStatus: 'green',
      targetTab: 'intelligence',
    });
  }

  // 5. Constraints (Phase 6)
  const constraints = intelligence?.constraint_signals || intelligence?.constraints || [];
  if (constraints.length > 0) {
    const topConstraint = constraints[0];
    highlights.push({
      id: 'hl-constraint',
      category: 'CONSTRAINT',
      categoryLabel: 'CONSTRAINT',
      title: topConstraint.title,
      description: topConstraint.description || 'Binding physical, regulatory, or faculty constraint identified.',
      badge: topConstraint.affected_area || 'Capacity',
      semanticStatus: 'amber',
      targetTab: 'intelligence',
    });
  }

  // 6. Execution Alerts (Phase 8: Review)
  if (latestReview) {
    const offTrack = latestReview.metric_variances?.find(
      (v) => v.status === 'OFF_TRACK' || v.status === 'AT_RISK'
    );
    if (offTrack) {
      highlights.push({
        id: 'hl-execution',
        category: 'EXECUTION_ALERT',
        categoryLabel: 'EXECUTION ALERT',
        title: `Variance Alert: ${offTrack.metric_key}`,
        description: `Variance observed against target: ${offTrack.variance_notation || 'Gap noted'}. Corrective action recommended.`,
        badge: offTrack.status.replace(/_/g, ' '),
        semanticStatus: offTrack.status === 'OFF_TRACK' ? 'red' : 'amber',
        targetTab: 'review',
      });
    }
  }

  // 7. Evidence Gaps / Limitations
  const dataGaps = currentPosition?.data_gaps || [];
  if (dataGaps.length > 0) {
    const topGap = dataGaps[0];
    highlights.push({
      id: 'hl-evidence-gap',
      category: 'EVIDENCE_GAP',
      categoryLabel: 'EVIDENCE GAP',
      title: topGap.title || 'Data Limitation Flagged',
      description: topGap.description || 'Insufficient verified evidence records available for this metric area.',
      badge: 'Insufficient Evidence',
      semanticStatus: 'blue',
      targetTab: 'overview',
    });
  }

  return (
    <div className="bg-white border border-[#D7E4EE] rounded-2xl p-4 flex flex-col h-full shadow-2xs">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#D7E4EE]">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-[#E8F4FB] text-[#163A63] rounded-lg">
            <Bell className="w-4 h-4 text-[#2F6EA6]" />
          </div>
          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#163A63]">
              HIGHLIGHTS
            </h3>
            <p className="text-[10px] text-[#6B7F91] font-medium">Real-time strategic signals</p>
          </div>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
          {highlights.length} Active Signals
        </span>
      </div>

      {/* Independently Scrollable Container */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 max-h-[calc(100vh-14rem)]">
        {highlights.length === 0 ? (
          <div className="p-6 text-center text-xs text-[#6B7F91] italic bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
            <Sparkles className="w-5 h-5 mx-auto text-[#6B7F91] mb-2" />
            No active strategic alerts detected from current evidence snapshot.
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

