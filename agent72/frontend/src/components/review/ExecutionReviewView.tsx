import React from 'react';
import { ExecutionReview, TargetVariance, CorrectiveActionCandidate } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { EmptyState } from '../common/EmptyState';
import { EvidencePanel } from '../common/EvidencePanel';
import { CheckSquare, AlertTriangle, HelpCircle, ArrowRight, ShieldCheck, Clock } from 'lucide-react';

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
  const diagnosticSignals: any[] = review.diagnostic_signals || [];
  const correctiveActions: CorrectiveActionCandidate[] = review.corrective_actions || [];

  return (
    <div className="space-y-6">
      <LeadershipDisclaimer />

      {/* Review Header Banner */}
      <div className="p-5 bg-white border border-[#D7E4EE] rounded-2xl shadow-2xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
                Phase 8 Execution Review
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#F5F9FC] text-[#19324A] border border-[#D7E4EE]">
                Period: {review.review_period}
              </span>
            </div>
            <h2 className="text-base font-bold text-[#163A63]">{review.progress_summary}</h2>
            <p className="text-xs text-[#6B7F91] mt-0.5">
              Review Date: {review.review_date} • Snapshot ID: {review.id.slice(0, 8)}...
            </p>
          </div>
          <StatusBadge status={review.overall_status} />
        </div>
      </div>

      {/* Target Variances Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckSquare className="w-4 h-4 text-[#163A63]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              Target Variances & Indicator Progress ({variances.length})
            </h3>
          </div>
          <span className="text-[11px] text-[#6B7F91]">
            Missing observations marked strictly as Insufficient Evidence
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {variances.map((v) => {
            const hasObs = v.observed_value !== null && v.observed_value !== undefined;
            const hasTarget = v.target_value !== null && v.target_value !== undefined;

            return (
              <div
                key={v.metric_key}
                className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="text-xs font-bold text-[#19324A] font-mono">{v.metric_key}</h4>
                    <span className="text-[11px] text-[#6B7F91]">
                      Direction: {v.direction ? v.direction.replace(/_/g, ' ') : 'HIGHER IS BETTER'}
                    </span>
                  </div>
                  <StatusBadge status={v.status} size="sm" />
                </div>

                <div className="grid grid-cols-3 gap-2 py-2 border-y border-[#D7E4EE] text-xs">
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-[#6B7F91] font-semibold">Target</div>
                    <div className="font-semibold text-[#19324A] mt-0.5">
                      {hasTarget ? `${v.target_value} ${v.unit || ''}` : <span className="text-[#6B7F91] italic">N/A</span>}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-[#6B7F91] font-semibold">Observed</div>
                    <div className="font-bold text-[#163A63] mt-0.5">
                      {hasObs ? (
                        `${v.observed_value} ${v.unit || ''}`
                      ) : (
                        <span className="text-[#6B7F91] text-[11px] font-semibold italic">Insufficient evidence</span>
                      )}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-[#6B7F91] font-semibold">Variance</div>
                    <div className="font-bold text-[#19324A] mt-0.5">
                      {v.variance_notation || 'N/A'}
                    </div>
                  </div>
                </div>

                {v.notes && (
                  <p className="text-[11px] text-[#6B7F91] leading-relaxed italic">
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
            <AlertTriangle className="w-4 h-4 text-[#B7791F]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              Diagnostic Execution Signals ({diagnosticSignals.length})
            </h3>
          </div>

          <div className="p-4 bg-[#FEF9C3] border border-[#FDE68A] rounded-xl space-y-2 text-xs">
            {diagnosticSignals.map((sig, idx) => {
              const text = typeof sig === 'string' ? sig : sig.description || sig.title || JSON.stringify(sig);
              return (
                <div key={idx} className="flex items-start gap-2 text-[#B7791F]">
                  <span className="font-bold">•</span>
                  <span className="leading-relaxed font-medium">{text}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Candidate Corrective Actions */}
      {correctiveActions.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#2F6EA6]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              Candidate Corrective Actions ({correctiveActions.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {correctiveActions.map((ca) => (
              <div
                key={ca.id}
                className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs space-y-2 text-xs"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-bold text-[#163A63]">{ca.title}</h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
                    {ca.signal_type}
                  </span>
                </div>

                <div className="text-[#19324A] font-semibold">
                  <span className="text-[#6B7F91] font-normal">Suggested Action: </span>
                  {ca.suggested_action}
                </div>

                <p className="text-[#6B7F91] text-[11px] leading-relaxed italic">
                  Rationale: {ca.rationale}
                </p>

                <div className="pt-2 border-t border-[#D7E4EE] flex items-center justify-between text-[11px] text-[#6B7F91]">
                  <span>Governance:</span>
                  <span className="font-bold text-[#B7791F]">
                    {ca.requires_leadership_approval ? 'Requires Leadership Approval' : 'Operational'}
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

