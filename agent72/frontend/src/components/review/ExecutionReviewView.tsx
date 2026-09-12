import React from 'react';
import { ExecutionReview, TargetVariance, CorrectiveActionCandidate } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { EmptyState } from '../common/EmptyState';
import { CheckSquare, AlertTriangle, HelpCircle, ArrowRight, ShieldCheck } from 'lucide-react';

interface ExecutionReviewViewProps {
  review?: ExecutionReview | null;
}

export const ExecutionReviewView: React.FC<ExecutionReviewViewProps> = ({ review }) => {
  if (!review) {
    return (
      <EmptyState
        title="No Execution Review Available"
        description="No periodic or annual execution review has been recorded yet for the active strategic plan."
      />
    );
  }

  const variances: TargetVariance[] = review.metric_variances || [];
  const diagnosticSignals: string[] = review.diagnostic_signals || [];
  const correctiveActions: CorrectiveActionCandidate[] = review.corrective_actions || [];

  return (
    <div className="space-y-6">
      <LeadershipDisclaimer />

      {/* Review Header Banner */}
      <div className="p-5 bg-white border border-slate-200 rounded-2xl shadow-2xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Periodic Execution Review
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                FY {review.review_period}
              </span>
            </div>
            <h2 className="text-base font-bold text-slate-900">{review.progress_summary}</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Review Date: {review.review_date} • Snapshot ID: {review.id.slice(0, 8)}...
            </p>
          </div>
          <StatusBadge status={review.overall_status} />
        </div>
      </div>

      {/* Target Variances Table */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <CheckSquare className="w-4 h-4 text-blue-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Target Variances & Indicator Evaluation ({variances.length})
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {variances.map((v) => {
            const hasObs = v.observed_value !== null && v.observed_value !== undefined;
            return (
              <div
                key={v.metric_key}
                className="p-4 bg-white rounded-xl border border-slate-200/90 shadow-2xs space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 font-mono">{v.metric_key}</h4>
                    <span className="text-[11px] text-slate-500">Direction: {v.direction || 'HIGHER_IS_BETTER'}</span>
                  </div>
                  <StatusBadge status={v.status} size="sm" />
                </div>

                <div className="grid grid-cols-3 gap-2 py-2 border-y border-slate-100 text-xs">
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Target</div>
                    <div className="font-semibold text-slate-800 mt-0.5">
                      {v.target_value !== null && v.target_value !== undefined
                        ? `${v.target_value} ${v.unit || ''}`
                        : 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Observed</div>
                    <div className="font-bold text-slate-900 mt-0.5">
                      {hasObs ? (
                        `${v.observed_value} ${v.unit || ''}`
                      ) : (
                        <span className="text-slate-400 italic">Insufficient evidence</span>
                      )}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Variance</div>
                    <div className="font-bold text-slate-800 mt-0.5">
                      {v.variance_notation}
                    </div>
                  </div>
                </div>

                {v.notes && (
                  <p className="text-[11px] text-slate-500 leading-relaxed italic">
                    {v.notes}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Diagnostic Signals */}
      {diagnosticSignals.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Diagnostic Execution Signals ({diagnosticSignals.length})
            </h3>
          </div>

          <div className="p-4 bg-amber-50/50 border border-amber-200/80 rounded-xl space-y-2 text-xs">
            {diagnosticSignals.map((sig, idx) => (
              <div key={idx} className="flex items-start gap-2 text-amber-900">
                <span className="font-bold">•</span>
                <span className="leading-relaxed">{sig}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Corrective Action Candidates */}
      {correctiveActions.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Candidate Corrective Actions ({correctiveActions.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {correctiveActions.map((ca) => (
              <div
                key={ca.id}
                className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs space-y-2 text-xs"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-bold text-slate-900">{ca.title}</h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200">
                    {ca.signal_type}
                  </span>
                </div>

                <div className="text-slate-700 font-medium">
                  <span className="text-slate-500 font-normal">Suggested Action: </span>
                  {ca.suggested_action}
                </div>

                <p className="text-slate-500 text-[11px] leading-relaxed italic">
                  Rationale: {ca.rationale}
                </p>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                  <span>Requires Leadership Approval:</span>
                  <span className="font-bold text-amber-700">
                    {ca.requires_leadership_approval ? 'Required' : 'Discretionary'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
