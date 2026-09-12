import React from 'react';
import { CurrentPositionAnalysis, MetricAssessment } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { EvidencePanel } from '../common/EvidencePanel';
import { EmptyState } from '../common/EmptyState';
import { ShieldAlert, CheckCircle, Database } from 'lucide-react';

interface CurrentPositionViewProps {
  analysis?: CurrentPositionAnalysis | null;
}

export const CurrentPositionView: React.FC<CurrentPositionViewProps> = ({ analysis }) => {
  if (!analysis || !analysis.metric_assessments?.length) {
    return (
      <EmptyState
        title="No Current Position Analysis Found"
        description="No baseline assessment snapshot has been generated for this institution in this period."
      />
    );
  }

  const formatGap = (m: MetricAssessment) => {
    if (m.gap === null || m.gap === undefined) {
      return <span className="text-slate-400 italic">No gap computed</span>;
    }
    const isPct = m.unit === '%' || m.unit === 'percent' || m.unit === 'percentage';
    const unitLabel = m.gap_unit_label || (isPct ? 'percentage points' : m.unit || '');
    const sign = m.gap > 0 ? '+' : '';
    const color = m.gap < 0 ? 'text-rose-600 font-semibold' : 'text-emerald-600 font-semibold';
    return (
      <span className={color}>
        {sign}{m.gap.toFixed(1)} {unitLabel}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-4 bg-white rounded-xl border border-slate-200">
        <div>
          <h2 className="text-base font-bold text-slate-900">{analysis.title}</h2>
          <p className="text-xs text-slate-500">
            Analysis Period: {analysis.analysis_period} • Snapshot ID: {analysis.id.slice(0, 8)}...
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg border border-blue-200">
            Overall Confidence: {Math.round((analysis.overall_confidence || 0.8) * 100)}%
          </span>
        </div>
      </div>

      {/* Metrics Assessment Cards */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Evaluated Institutional Indicators ({analysis.metric_assessments.length})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {analysis.metric_assessments.map((m) => {
            const hasData = m.observed_value !== null && m.observed_value !== undefined;
            return (
              <div
                key={m.metric_key}
                className="p-4 bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">
                      {m.metric_name || m.metric_key}
                    </h4>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {m.metric_key}
                    </span>
                  </div>
                  <StatusBadge status={m.performance_band || (hasData ? 'ACTIVE' : 'INSUFFICIENT_EVIDENCE')} />
                </div>

                <div className="grid grid-cols-3 gap-2 py-2.5 my-2 border-y border-slate-100 text-xs">
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Observed</div>
                    <div className="font-bold text-slate-900 mt-0.5">
                      {hasData ? `${m.observed_value} ${m.unit || ''}` : <span className="text-slate-400 italic">Insufficient evidence</span>}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Target</div>
                    <div className="font-semibold text-slate-700 mt-0.5">
                      {m.target_value !== null && m.target_value !== undefined
                        ? `${m.target_value} ${m.unit || ''}`
                        : 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Variance / Gap</div>
                    <div className="mt-0.5">{formatGap(m)}</div>
                  </div>
                </div>

                <EvidencePanel
                  evidenceIds={m.evidence_ids}
                  findings={m.findings}
                  confidence={m.confidence}
                  qualityTier={m.data_quality_tier}
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
