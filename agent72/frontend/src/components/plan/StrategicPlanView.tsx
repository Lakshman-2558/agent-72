import React from 'react';
import { StrategicPlan } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { EmptyState } from '../common/EmptyState';
import { FileCheck, Flag, CheckCircle2, Clock, Users, ArrowRight } from 'lucide-react';

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
    return `Gap required: ${sign}${tgt.gap.toFixed(1)} ${unitLabel}`;
  };

  const formatBaseline = (tgt: any) => {
    if (tgt.baseline_value === null || tgt.baseline_value === undefined) return 'N/A';
    return `${tgt.baseline_value}${tgt.unit || ''}`;
  };

  const formatTarget = (tgt: any) => {
    if (tgt.target_value === null || tgt.target_value === undefined) return 'N/A';
    const period = tgt.target_period ? ` (${tgt.target_period})` : ' (2030)';
    return `${tgt.target_value}${tgt.unit || ''}${period}`;
  };

  return (
    <div className="space-y-6">
      <LeadershipDisclaimer />

      {/* Plan Header Card */}
      <div className="p-5 bg-white border border-slate-200 rounded-2xl shadow-2xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <StatusBadge status={plan.status} />
              <span className="text-xs text-slate-500 font-semibold">
                Horizon: {plan.horizon_start_year} – {plan.horizon_end_year}
              </span>
            </div>
            <h2 className="text-lg font-extrabold text-slate-900">{plan.title}</h2>
            {plan.institution_name && (
              <p className="text-xs text-slate-500 mt-0.5">{plan.institution_name}</p>
            )}
          </div>
          <div className="text-xs font-semibold px-3 py-1.5 bg-blue-50 text-blue-800 rounded-xl border border-blue-200 self-start sm:self-center">
            {objectives.length} Strategic Objectives
          </div>
        </div>
      </div>

      {/* Hierarchical Structure */}
      <div className="space-y-5">
        <div className="flex items-center gap-2">
          <FileCheck className="w-4 h-4 text-blue-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Plan Execution Hierarchy
          </h3>
        </div>

        {objectives.map((obj, oIdx) => (
          <div
            key={obj.id}
            className="p-5 bg-white border border-slate-200 rounded-2xl shadow-2xs space-y-4"
          >
            {/* 1. Objective Header */}
            <div className="flex items-start justify-between gap-3 pb-3 border-b border-slate-100">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-extrabold px-2 py-0.5 rounded bg-blue-100 text-blue-800 uppercase">
                    Objective {oIdx + 1}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-slate-500 font-medium">
                    <Users className="w-3.5 h-3.5 text-slate-400" />
                    <span>Lead Unit: {obj.owner_unit_id || obj.owner || 'TO_BE_ASSIGNED'}</span>
                  </div>
                </div>
                <h4 className="text-sm font-bold text-slate-900">{obj.title}</h4>
                {obj.strategic_rationale && (
                  <p className="text-xs text-slate-600 leading-relaxed">{obj.strategic_rationale}</p>
                )}
              </div>
              <StatusBadge status={obj.status || 'PLANNED'} size="sm" />
            </div>

            {/* 2. Targets Hierarchy */}
            {obj.targets && obj.targets.length > 0 && (
              <div className="space-y-2 pl-2 border-l-2 border-blue-200">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                  <Flag className="w-3 h-3 text-blue-600" />
                  Measurable Strategic Targets ({obj.targets.length})
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {obj.targets.map((tgt) => (
                    <div key={tgt.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 text-xs">
                      <div className="font-bold text-slate-800 font-mono text-[11px]">
                        {tgt.metric_key}
                      </div>
                      <div className="flex items-center gap-2 mt-1.5 text-slate-700">
                        <span>Baseline: {formatBaseline(tgt)}</span>
                        <ArrowRight className="w-3 h-3 text-slate-400" />
                        <span className="font-bold text-blue-700">
                          Target: {formatTarget(tgt)}
                        </span>
                      </div>
                      {tgt.gap !== null && tgt.gap !== undefined && (
                        <div className="text-[11px] text-slate-500 mt-1">
                          {formatTargetGap(tgt)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 3. Initiatives & Milestones Hierarchy */}
            {obj.initiatives && obj.initiatives.length > 0 && (
              <div className="space-y-3 pl-2 border-l-2 border-indigo-200">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-indigo-600" />
                  Execution Initiatives ({obj.initiatives.length})
                </div>

                <div className="space-y-3">
                  {obj.initiatives.map((init) => (
                    <div key={init.id} className="p-3.5 bg-slate-50/70 rounded-xl border border-slate-200 text-xs space-y-2.5">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="font-bold text-slate-900">{init.title}</div>
                          <div className="text-[11px] text-slate-500 mt-0.5">
                            Owner: {init.owner_unit_id || init.unit_owner || 'TO_BE_ASSIGNED'} • Resources: {init.resource_requirement || 'UNKNOWN'}
                          </div>
                        </div>
                        <StatusBadge status={init.status || 'PLANNED'} size="sm" />
                      </div>

                      {/* Milestones */}
                      {init.milestones && init.milestones.length > 0 && (
                        <div className="space-y-1.5 pt-2 border-t border-slate-200/70">
                          <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                            <Clock className="w-3 h-3 text-slate-400" />
                            Milestone Schedule
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {init.milestones.map((m) => (
                              <div
                                key={m.id}
                                className="p-2 bg-white rounded-lg border border-slate-200/80 text-[11px] flex items-center justify-between"
                              >
                                <span className="font-medium text-slate-800 truncate pr-2">{m.title}</span>
                                <span className="text-[10px] font-semibold text-slate-500 shrink-0 bg-slate-100 px-1.5 py-0.5 rounded">
                                  {m.due_period || 'Period TBD'}
                                </span>
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
