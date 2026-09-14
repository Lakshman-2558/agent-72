import React from 'react';
import { StrategicPlan } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { EmptyState } from '../common/EmptyState';
import { EvidencePanel } from '../common/EvidencePanel';
import { FileCheck, Flag, CheckCircle2, Clock, Users, ArrowRight, Building } from 'lucide-react';

interface StrategicPlanViewProps {
  plan?: StrategicPlan | null;
}

export const StrategicPlanView: React.FC<StrategicPlanViewProps> = ({ plan }) => {
  if (!plan) {
    return (
      <EmptyState
        title="No Strategic Plan Active"
        description="No institutional strategic plan has been finalized or activated for this institution."
      />
    );
  }

  const objectives = plan.objectives || [];

  const formatTargetGap = (tgt: any) => {
    if (tgt.gap === null || tgt.gap === undefined) return null;
    const isPct = tgt.unit === '%' || tgt.unit === 'percent' || tgt.unit === 'percentage';
    const unitLabel = tgt.gap_unit_label || (isPct ? 'percentage points' : tgt.unit || '');
    const sign = tgt.gap > 0 ? '+' : '';
    return `Required Gap: ${sign}${tgt.gap.toFixed(1)} ${unitLabel}`;
  };

  const formatBaseline = (tgt: any) => {
    if (tgt.baseline_value === null || tgt.baseline_value === undefined) return 'Insufficient evidence';
    return `${tgt.baseline_value} ${tgt.unit || ''}`;
  };

  const formatTarget = (tgt: any) => {
    if (tgt.target_value === null || tgt.target_value === undefined) return 'Insufficient evidence';
    const period = tgt.target_period ? ` (${tgt.target_period})` : '';
    return `${tgt.target_value} ${tgt.unit || ''}${period}`;
  };

  return (
    <div className="space-y-6">
      <LeadershipDisclaimer />

      {/* Plan Header Card */}
      <div className="p-5 bg-white border border-[#D7E4EE] rounded-2xl shadow-2xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
                Phase 8 Plan
              </span>
              <StatusBadge status={plan.status} size="sm" />
              <span className="text-xs text-[#6B7F91] font-semibold">
                Horizon: {plan.horizon_start_year} – {plan.horizon_end_year}
              </span>
            </div>
            <h2 className="text-lg font-bold text-[#163A63]">{plan.title}</h2>
            {plan.institution_name && (
              <p className="text-xs text-[#6B7F91] mt-0.5">{plan.institution_name}</p>
            )}
          </div>
          <div className="text-xs font-bold px-3 py-1.5 bg-[#E8F4FB] text-[#163A63] rounded-xl border border-[#D7E4EE] self-start sm:self-center">
            {objectives.length} Strategic Objectives
          </div>
        </div>
      </div>

      {/* Hierarchy: Plan → Objectives → Targets → Initiatives → Milestones */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-[#163A63]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              Strategic Plan Execution Hierarchy
            </h3>
          </div>
          <span className="text-[11px] text-[#6B7F91]">
            Strategic Plan ↓ Objectives ↓ Targets ↓ Initiatives ↓ Milestones
          </span>
        </div>

        {objectives.map((obj, oIdx) => (
          <div
            key={obj.id}
            className="p-5 bg-white border border-[#D7E4EE] rounded-2xl shadow-2xs space-y-4"
          >
            {/* 1. Objective Header */}
            <div className="flex items-start justify-between gap-3 pb-3 border-b border-[#D7E4EE]">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10.5px] font-bold px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE] uppercase">
                    Objective {oIdx + 1}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-[#6B7F91] font-medium">
                    <Building className="w-3.5 h-3.5 text-[#2F6EA6]" />
                    <span>Lead Unit: {obj.owner_unit_id || obj.owner || 'To be assigned'}</span>
                  </div>
                </div>
                <h4 className="text-sm font-bold text-[#19324A]">{obj.title}</h4>
                {obj.strategic_rationale && (
                  <p className="text-xs text-[#6B7F91] leading-relaxed">{obj.strategic_rationale}</p>
                )}
              </div>
              <StatusBadge status={obj.status || 'PLANNED'} size="sm" />
            </div>

            {/* 2. Targets Hierarchy */}
            {obj.targets && obj.targets.length > 0 && (
              <div className="space-y-2 pl-3 border-l-2 border-[#2F6EA6]">
                <div className="text-[11px] font-bold uppercase tracking-wider text-[#163A63] flex items-center gap-1.5">
                  <Flag className="w-3.5 h-3.5 text-[#2F6EA6]" />
                  Measurable Strategic Targets ({obj.targets.length})
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {obj.targets.map((tgt) => (
                    <div key={tgt.id} className="p-3 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE] text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[#163A63] font-mono text-[11px]">
                          {tgt.metric_key}
                        </span>
                        <StatusBadge status={tgt.status || 'PROPOSED_TARGET'} size="sm" />
                      </div>
                      <div className="flex items-center gap-2 text-[#19324A] text-[11.5px] pt-1">
                        <span>Baseline: {formatBaseline(tgt)}</span>
                        <ArrowRight className="w-3 h-3 text-[#6B7F91]" />
                        <span className="font-bold text-[#2F6EA6]">
                          Target: {formatTarget(tgt)}
                        </span>
                      </div>
                      {tgt.direction && (
                        <div className="text-[10.5px] text-[#6B7F91]">
                          Direction: {tgt.direction.replace(/_/g, ' ')}
                        </div>
                      )}
                      {tgt.gap !== null && tgt.gap !== undefined && (
                        <div className="text-[11px] text-[#2F6EA6] font-semibold">
                          {formatTargetGap(tgt)}
                        </div>
                      )}
                      <EvidencePanel evidenceIds={tgt.evidence_ids} confidence={tgt.confidence} />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 3. Initiatives & Milestones Hierarchy */}
            {obj.initiatives && obj.initiatives.length > 0 && (
              <div className="space-y-3 pl-3 border-l-2 border-[#163A63]">
                <div className="text-[11px] font-bold uppercase tracking-wider text-[#163A63] flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#163A63]" />
                  Execution Initiatives ({obj.initiatives.length})
                </div>

                <div className="space-y-3">
                  {obj.initiatives.map((init) => (
                    <div key={init.id} className="p-3.5 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE] text-xs space-y-2.5">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="font-bold text-[#19324A]">{init.title}</div>
                          <div className="text-[11px] text-[#6B7F91] mt-0.5">
                            Owner: {init.owner_unit_id || init.unit_owner || 'To be assigned'} • Resource Requirement: {init.resource_requirement || 'To be assigned'}
                          </div>
                        </div>
                        <StatusBadge status={init.status || 'PLANNED'} size="sm" />
                      </div>

                      {/* Milestones */}
                      {init.milestones && init.milestones.length > 0 && (
                        <div className="space-y-1.5 pt-2 border-t border-[#D7E4EE]">
                          <div className="text-[10px] font-bold uppercase tracking-wider text-[#6B7F91] flex items-center gap-1">
                            <Clock className="w-3 h-3 text-[#2F6EA6]" />
                            Milestone Schedule
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {init.milestones.map((m) => (
                              <div
                                key={m.id}
                                className="p-2 bg-white rounded-lg border border-[#D7E4EE] text-[11px] flex items-center justify-between"
                              >
                                <span className="font-medium text-[#19324A] truncate pr-2">{m.title}</span>
                                <div className="flex items-center gap-1 shrink-0">
                                  <span className="text-[10px] font-semibold text-[#6B7F91] bg-[#F5F9FC] border border-[#D7E4EE] px-1.5 py-0.5 rounded">
                                    {m.due_period || 'Period TBD'}
                                  </span>
                                  <StatusBadge status={m.status || 'NOT_STARTED'} size="sm" />
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

