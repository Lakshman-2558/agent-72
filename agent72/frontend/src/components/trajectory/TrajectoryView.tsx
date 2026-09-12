import React from 'react';
import { TrajectoryAnalysis, MetricTrajectory } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { EmptyState } from '../common/EmptyState';
import { TrendingUp, TrendingDown, Minus, Activity, HelpCircle } from 'lucide-react';

interface TrajectoryViewProps {
  analysis?: TrajectoryAnalysis | null;
}

export const TrajectoryView: React.FC<TrajectoryViewProps> = ({ analysis }) => {
  if (!analysis || !analysis.metric_trajectories?.length) {
    return (
      <EmptyState
        title="No Trajectory Analysis Found"
        description="No multi-period longitudinal trajectory snapshot has been generated for this institution."
      />
    );
  }

  const getDirectionIcon = (status: string) => {
    switch (status) {
      case 'IMPROVING':
        return <TrendingUp className="w-4 h-4 text-emerald-600" />;
      case 'DECLINING':
        return <TrendingDown className="w-4 h-4 text-rose-600" />;
      case 'VOLATILE':
        return <Activity className="w-4 h-4 text-amber-600" />;
      case 'STABLE':
        return <Minus className="w-4 h-4 text-slate-500" />;
      default:
        return <HelpCircle className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Context Banner */}
      <div className="p-4 bg-sky-50/70 border border-sky-200/80 rounded-xl text-xs text-sky-900 flex items-start gap-2">
        <TrendingUp className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Longitudinal Trajectory Boundary: </span>
          <span>
            Trajectory establishes where the institution is heading across canonical academic periods.
            It isolates momentum, stability, and deceleration without substituting strategic choices.
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Tracked Directional Trajectories ({analysis.metric_trajectories.length})
          </h3>
          <span className="text-xs text-slate-500">
            Overall Confidence: {Math.round((analysis.overall_confidence || 0.8) * 100)}%
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {analysis.metric_trajectories.map((t) => {
            const hasChange = t.net_change !== null && t.net_change !== undefined;
            return (
              <div
                key={t.metric_key}
                className="p-4 bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-slate-100 rounded-lg">
                      {getDirectionIcon(t.status)}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">{t.metric_name || t.metric_key}</h4>
                      <span className="text-[11px] text-slate-400 font-mono">{t.metric_key}</span>
                    </div>
                  </div>
                  <StatusBadge status={t.status} />
                </div>

                <div className="grid grid-cols-3 gap-2 py-2 border-y border-slate-100 text-xs">
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Net Change</div>
                    <div className="font-bold text-slate-900 mt-0.5">
                      {hasChange && t.net_change !== null && t.net_change !== undefined
                        ? `${t.net_change > 0 ? '+' : ''}${t.net_change.toFixed(1)} ${t.unit || ''}`
                        : <span className="text-slate-400 italic">Insufficient data</span>}
                    </div>
                  </div>

                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Observations</div>
                    <div className="font-semibold text-slate-700 mt-0.5">
                      {t.observation_count} Periods
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Consistency</div>
                    <div className="font-semibold text-slate-700 mt-0.5">
                      {t.consistency_score !== undefined ? `${Math.round(t.consistency_score * 100)}%` : 'N/A'}
                    </div>
                  </div>
                </div>

                {t.findings && t.findings.length > 0 && (
                  <div className="space-y-1 text-xs text-slate-600">
                    {t.findings.map((f, idx) => (
                      <p key={idx} className="line-clamp-2 leading-relaxed">
                        • {f}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
