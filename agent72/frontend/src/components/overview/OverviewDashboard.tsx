import React, { useState } from 'react';
import {
  Target,
  TrendingUp,
  AlertTriangle,
  Lock,
  Lightbulb,
  Globe,
  Split,
  FileCheck,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  HelpCircle,
} from 'lucide-react';
import {
  CurrentPositionAnalysis,
  TrajectoryAnalysis,
  StrategicIntelligenceAnalysis,
  StrategicOptionsAnalysis,
  StrategicPlan,
  ExecutionReview,
} from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  Cell,
  PieChart,
  Pie,
} from 'recharts';

interface OverviewDashboardProps {
  currentPosition?: CurrentPositionAnalysis | null;
  trajectory?: TrajectoryAnalysis | null;
  intelligence?: StrategicIntelligenceAnalysis | null;
  options?: StrategicOptionsAnalysis | null;
  plan?: StrategicPlan | null;
  latestReview?: ExecutionReview | null;
  onNavigateTab: (tab: string) => void;
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  currentPosition,
  trajectory,
  intelligence,
  options,
  plan,
  latestReview,
  onNavigateTab,
}) => {
  // Extract key metrics from current position and cross-reference with trajectory
  const rawMetrics = currentPosition?.key_metrics || currentPosition?.metric_assessments || [];
  const trajectories = trajectory?.metric_trends || trajectory?.metric_trajectories || [];
  const trajMap = new Map<string, any>(trajectories.map((t: any) => [t.metric_key, t]));

  // Selected metric for trajectory line chart
  const [selectedTrajectoryMetricKey, setSelectedTrajectoryMetricKey] = useState<string>(
    trajectories.length > 0 ? trajectories[0].metric_key : ''
  );

  // 1. Chart 1: Current vs Target (BarChart)
  const currentVsTargetData = rawMetrics
    .filter((m: any) => m.observed_value !== null && m.observed_value !== undefined)
    .slice(0, 6)
    .map((m: any) => ({
      name: (m.metric_name || m.metric_key).replace(/_/g, ' ').slice(0, 16),
      observed: m.observed_value,
      target: m.target_value ?? 0,
      unit: m.unit || '',
    }));

  // 2. Chart 2: Longitudinal Metric Trajectory (LineChart)
  const activeTrajMetric =
    trajectories.find((t: any) => t.metric_key === selectedTrajectoryMetricKey) ||
    trajectories[0];

  const trajectoryChartData = (activeTrajMetric as any)?.observations
    ? (activeTrajMetric as any).observations.map((obs: any) => ({
        period: obs.period,
        value: obs.numeric_value,
      }))
    : activeTrajMetric?.historical_points
    ? activeTrajMetric.historical_points.map((pt: any) => ({
        period: pt.period,
        value: pt.value,
      }))
    : [];

  // 3. Chart 3: Strategic Issue Distribution (PieChart)
  const issuesData = [
    {
      name: 'Strategic Risks',
      value: (intelligence?.risk_signals || intelligence?.risks || []).length,
      color: '#C44B55',
    },
    {
      name: 'Constraints',
      value: (intelligence?.constraint_signals || intelligence?.constraints || []).length,
      color: '#B7791F',
    },
    {
      name: 'Opportunities',
      value: (intelligence?.opportunity_signals || intelligence?.opportunities || []).length,
      color: '#16805C',
    },
    {
      name: 'External Factors',
      value: (intelligence?.external_factors || []).length,
      color: '#2F6EA6',
    },
  ].filter((item) => item.value > 0);

  // 4. Chart 4: Strategic Option Comparison across 7 dimensions (BarChart)
  const optionComparisonData = (options?.options || []).slice(0, 5).map((opt: any) => ({
    name: opt.title.length > 18 ? `${opt.title.slice(0, 16)}...` : opt.title,
    score: typeof opt.total_score === 'number' ? opt.total_score : 0,
    alignment: opt.evaluation?.strategic_alignment_score ?? 15,
    impact: opt.evaluation?.impact_score ?? 15,
    feasibility: opt.evaluation?.feasibility_score ?? 10,
  }));

  // 5. Chart 5: Execution Target Variance (BarChart)
  const executionVarianceData = (latestReview?.metric_variances || [])
    .filter((v) => v.absolute_variance !== null && v.absolute_variance !== undefined)
    .slice(0, 6)
    .map((v) => ({
      name: v.metric_key.replace(/_/g, ' ').slice(0, 14),
      variance: v.absolute_variance ?? 0,
      status: v.status,
    }));

  const formatGapText = (m: any) => {
    if (m.target_value === null || m.target_value === undefined) return 'No target configured';
    if (m.observed_value === null || m.observed_value === undefined) return 'Insufficient evidence';
    const isPct = m.unit === '%' || m.unit === 'percent' || m.unit === 'percentage';
    const unitLabel = isPct ? 'percentage points' : m.unit || '';
    const gap = (m.observed_value - m.target_value);
    const sign = gap > 0 ? '+' : '';
    if (gap < 0) {
      return `${Math.abs(gap).toFixed(1)} ${unitLabel} below target`;
    } else if (gap > 0) {
      return `${sign}${gap.toFixed(1)} ${unitLabel} above target`;
    }
    return `Met target (${m.target_value} ${m.unit || ''})`;
  };

  return (
    <div className="space-y-6">
      <LeadershipDisclaimer />

      {/* Executive Key Indicators Grid */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#163A63]">
            Executive Strategic Indicators
          </h3>
          <span className="text-[11px] text-[#6B7F91]">
            Source: Phase 4 Baseline & Phase 5 Trajectory Engine
          </span>
        </div>

        {rawMetrics.length === 0 ? (
          <div className="p-6 bg-white rounded-2xl border border-[#D7E4EE] text-center text-xs text-[#6B7F91] italic">
            Insufficient evidence records observed for institutional KPIs.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {rawMetrics.slice(0, 6).map((m: any) => {
              const hasObs = m.observed_value !== null && m.observed_value !== undefined;
              const hasPrev = m.previous_value !== null && m.previous_value !== undefined;
              const traj = trajMap.get(m.metric_key);
              const isImproving = traj?.status === 'IMPROVING' || m.change_direction === 'POSITIVE';
              const isDeclining = traj?.status === 'DECLINING' || m.change_direction === 'NEGATIVE';

              return (
                <div
                  key={m.metric_key}
                  className="p-4 bg-white rounded-2xl border border-[#D7E4EE] shadow-2xs hover:shadow-xs transition space-y-2.5 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="text-xs font-bold text-[#19324A] leading-snug">
                          {m.metric_name || m.metric_key}
                        </h4>
                        <span className="text-[10.5px] font-mono text-[#6B7F91]">
                          {m.metric_key}
                        </span>
                      </div>
                      <StatusBadge
                        status={
                          m.performance_band ||
                          m.performance_status ||
                          (hasObs ? 'ON_TRACK' : 'INSUFFICIENT_EVIDENCE')
                        }
                        size="sm"
                      />
                    </div>

                    <div className="flex items-baseline gap-2 mt-2">
                      <span className="text-2xl font-extrabold text-[#163A63]">
                        {hasObs ? `${m.observed_value} ${m.unit || ''}` : <span className="text-sm font-semibold text-[#6B7F91]">Insufficient evidence</span>}
                      </span>
                      {hasPrev && (
                        <span className="text-[11px] text-[#6B7F91]">
                          prev: {m.previous_value} {m.unit || ''}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-[#D7E4EE] space-y-1 text-xs">
                    {/* Direction & Target Gap */}
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-[#6B7F91]">Target: {m.target_value !== null && m.target_value !== undefined ? `${m.target_value} ${m.unit || ''}` : 'N/A'}</span>
                      <span className="font-semibold text-[#19324A] flex items-center gap-0.5">
                        {isImproving && <ArrowUpRight className="w-3.5 h-3.5 text-[#16805C]" />}
                        {isDeclining && <ArrowDownRight className="w-3.5 h-3.5 text-[#C44B55]" />}
                        {!isImproving && !isDeclining && <Minus className="w-3.5 h-3.5 text-[#6B7F91]" />}
                        <span className={isImproving ? 'text-[#16805C]' : isDeclining ? 'text-[#C44B55]' : 'text-[#6B7F91]'}>
                          {traj?.status ? traj.status.replace(/_/g, ' ') : 'Tracked'}
                        </span>
                      </span>
                    </div>

                    <div className="text-[11px] font-semibold text-[#2F6EA6]">
                      {formatGapText(m)}
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-[#6B7F91] pt-1">
                      <span>Confidence: {Math.round((m.confidence ?? 0.8) * 100)}%</span>
                      <span>Tier: {m.data_quality_tier || m.quality_tier || 'VERIFIED'}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Chart Section 1: Current vs Target & Longitudinal Trajectory */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Chart 1: Current vs Target */}
        <div className="p-4 bg-white rounded-2xl border border-[#D7E4EE] shadow-2xs">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#D7E4EE]">
            <div>
              <h4 className="text-xs font-bold text-[#163A63] uppercase tracking-wider">
                Current Observed vs Target Benchmark
              </h4>
              <p className="text-[10.5px] text-[#6B7F91]">
                Baseline observations vs configured leadership targets
              </p>
            </div>
            <span className="text-[11px] font-semibold text-[#2F6EA6] bg-[#E8F4FB] px-2 py-0.5 rounded border border-[#D7E4EE]">
              Phase 4 Baseline
            </span>
          </div>

          {currentVsTargetData.length === 0 ? (
            <div className="h-56 flex items-center justify-center text-xs text-[#6B7F91] italic">
              Insufficient metric observation data.
            </div>
          ) : (
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={currentVsTargetData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E8F4FB" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#6B7F91' }} interval={0} angle={-15} textAnchor="end" />
                  <YAxis tick={{ fontSize: 10, fill: '#6B7F91' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #D7E4EE', fontSize: '11px', color: '#19324A' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Bar dataKey="observed" fill="#163A63" name="Observed Value" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="target" fill="#2F6EA6" name="Target Benchmark" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Chart 2: Metric Trajectory Line Chart */}
        <div className="p-4 bg-white rounded-2xl border border-[#D7E4EE] shadow-2xs">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#D7E4EE]">
            <div>
              <h4 className="text-xs font-bold text-[#163A63] uppercase tracking-wider">
                Longitudinal Metric Trajectory
              </h4>
              <p className="text-[10.5px] text-[#6B7F91]">
                Multi-period directional movement and momentum
              </p>
            </div>
            {trajectories.length > 0 && (
              <select
                value={selectedTrajectoryMetricKey}
                onChange={(e) => setSelectedTrajectoryMetricKey(e.target.value)}
                className="text-xs bg-[#F5F9FC] border border-[#D7E4EE] text-[#163A63] font-semibold rounded-lg px-2 py-1 focus:outline-none"
              >
                {trajectories.map((t: any) => (
                  <option key={t.metric_key} value={t.metric_key}>
                    {t.metric_name || t.metric_key}
                  </option>
                ))}
              </select>
            )}
          </div>

          {trajectoryChartData.length === 0 ? (
            <div className="h-56 flex items-center justify-center text-xs text-[#6B7F91] italic">
              Insufficient historical observations for selected trajectory.
            </div>
          ) : (
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trajectoryChartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E8F4FB" />
                  <XAxis dataKey="period" tick={{ fontSize: 10, fill: '#6B7F91' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#6B7F91' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #D7E4EE', fontSize: '11px', color: '#19324A' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#16805C"
                    strokeWidth={2.5}
                    dot={{ r: 4, fill: '#16805C' }}
                    name={activeTrajMetric?.metric_name || activeTrajMetric?.metric_key || 'Observed Value'}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Chart Section 2: Strategic Issues Distribution & Strategic Options Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Chart 3: Strategic Issues Distribution */}
        <div className="p-4 bg-white rounded-2xl border border-[#D7E4EE] shadow-2xs lg:col-span-1">
          <div className="pb-2 mb-3 border-b border-[#D7E4EE]">
            <h4 className="text-xs font-bold text-[#163A63] uppercase tracking-wider">
              Strategic Signal Distribution
            </h4>
            <p className="text-[10.5px] text-[#6B7F91]">
              Phase 6 intelligence breakdown
            </p>
          </div>

          {issuesData.length === 0 ? (
            <div className="h-56 flex items-center justify-center text-xs text-[#6B7F91] italic">
              No strategic issues recorded.
            </div>
          ) : (
            <div className="h-60 w-full flex flex-col items-center justify-center">
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={issuesData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {issuesData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #D7E4EE', fontSize: '11px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-wrap gap-2 justify-center text-[10.5px] font-semibold text-[#19324A] pt-1">
                {issuesData.map((item, i) => (
                  <span key={i} className="flex items-center gap-1">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                    {item.name} ({item.value})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Chart 4: Option Evaluation Comparison */}
        <div className="p-4 bg-white rounded-2xl border border-[#D7E4EE] shadow-2xs lg:col-span-2">
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-[#D7E4EE]">
            <div>
              <h4 className="text-xs font-bold text-[#163A63] uppercase tracking-wider">
                Strategic Options Evaluation Comparison
              </h4>
              <p className="text-[10.5px] text-[#6B7F91]">
                Phase 7 deterministic multi-criteria scoring
              </p>
            </div>
            <button
              onClick={() => onNavigateTab('options')}
              className="text-xs font-bold text-[#2F6EA6] hover:underline"
            >
              View Options →
            </button>
          </div>

          {optionComparisonData.length === 0 ? (
            <div className="h-56 flex items-center justify-center text-xs text-[#6B7F91] italic">
              No strategic options evaluated.
            </div>
          ) : (
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={optionComparisonData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E8F4FB" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#6B7F91' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#6B7F91' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #D7E4EE', fontSize: '11px', color: '#19324A' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Bar dataKey="score" fill="#163A63" name="Total Score" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="alignment" fill="#2F6EA6" name="Alignment" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="impact" fill="#16805C" name="Impact" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Chart 5: Execution Target Variance (When latest review exists) */}
      {latestReview && (
        <div className="p-4 bg-white rounded-2xl border border-[#D7E4EE] shadow-2xs">
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-[#D7E4EE]">
            <div>
              <h4 className="text-xs font-bold text-[#163A63] uppercase tracking-wider">
                Execution Target Variance Analysis
              </h4>
              <p className="text-[10.5px] text-[#6B7F91]">
                Observed vs planned target absolute variances in FY {latestReview.review_period}
              </p>
            </div>
            <StatusBadge status={latestReview.overall_status} size="sm" />
          </div>

          {executionVarianceData.length === 0 ? (
            <div className="h-40 flex items-center justify-center text-xs text-[#6B7F91] italic">
              No measurable variance records in latest review.
            </div>
          ) : (
            <div className="h-52 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={executionVarianceData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E8F4FB" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#6B7F91' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#6B7F91' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #D7E4EE', fontSize: '11px', color: '#19324A' }}
                  />
                  <Bar dataKey="variance" fill="#B7791F" name="Absolute Variance" radius={[4, 4, 0, 0]}>
                    {executionVarianceData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.status === 'OFF_TRACK' ? '#C44B55' : entry.status === 'AT_RISK' ? '#B7791F' : '#16805C'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

