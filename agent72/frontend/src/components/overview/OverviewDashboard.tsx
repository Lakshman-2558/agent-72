import React from 'react';
import {
  Target,
  TrendingUp,
  AlertTriangle,
  Lock,
  Lightbulb,
  Globe,
  Split,
  FileCheck,
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
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

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
  // Metric chart data from assessments
  const chartData = (currentPosition?.metric_assessments || [])
    .filter((m) => m.observed_value !== null && m.observed_value !== undefined)
    .slice(0, 5)
    .map((m) => ({
      name: (m.metric_name || m.metric_key).replace(/_/g, ' ').slice(0, 16),
      observed: m.observed_value,
      target: m.target_value ?? 0,
      unit: m.unit || '',
    }));

  const risksCount = intelligence?.risks?.length ?? 0;
  const highRisksCount = intelligence?.risks?.filter((r) => r.severity === 'HIGH' || r.severity === 'CRITICAL').length ?? 0;
  const constraintsCount = intelligence?.constraints?.length ?? 0;
  const oppsCount = intelligence?.opportunities?.length ?? 0;
  const externalCount = intelligence?.external_factors?.length ?? 0;
  const optionsCount = options?.options?.length ?? 0;

  return (
    <div className="space-y-6">
      <LeadershipDisclaimer />

      {/* High-Level Executive Status Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        {/* Card 1: Current Position */}
        <div
          onClick={() => onNavigateTab('position')}
          className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition cursor-pointer flex flex-col justify-between"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Current Position</span>
            <Target className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-3">
            <div className="text-xl font-extrabold text-slate-900">
              {currentPosition?.metric_assessments?.length ?? 0} Assessed
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              Confidence: {Math.round((currentPosition?.overall_confidence || 0.8) * 100)}%
            </div>
          </div>
        </div>

        {/* Card 2: Trajectory */}
        <div
          onClick={() => onNavigateTab('trajectory')}
          className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition cursor-pointer flex flex-col justify-between"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Trajectory</span>
            <TrendingUp className="w-4 h-4 text-sky-600" />
          </div>
          <div className="mt-3">
            <div className="text-xl font-extrabold text-slate-900">
              {trajectory?.metric_trajectories?.length ?? 0} Indicators
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              Longitudinal tracking
            </div>
          </div>
        </div>

        {/* Card 3: Strategic Risks */}
        <div
          onClick={() => onNavigateTab('intelligence')}
          className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition cursor-pointer flex flex-col justify-between"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Strategic Risks</span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="mt-3">
            <div className="text-xl font-extrabold text-slate-900">
              {risksCount} Total
            </div>
            <div className="text-xs text-rose-600 font-semibold mt-0.5">
              {highRisksCount} High / Critical
            </div>
          </div>
        </div>

        {/* Card 4: Plan Status */}
        <div
          onClick={() => onNavigateTab('plan')}
          className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition cursor-pointer flex flex-col justify-between"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Plan Status</span>
            <FileCheck className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-3">
            <div className="text-base font-extrabold text-slate-900 truncate">
              {plan ? plan.status : 'NO ACTIVE PLAN'}
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              {plan ? `${plan.horizon_start_year}–${plan.horizon_end_year}` : 'Pending generation'}
            </div>
          </div>
        </div>
      </div>

      {/* Secondary Status Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        <div
          onClick={() => onNavigateTab('intelligence')}
          className="p-3 bg-white rounded-xl border border-slate-200/90 shadow-2xs cursor-pointer flex items-center gap-3"
        >
          <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
            <Lock className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Constraints</div>
            <div className="text-sm font-bold text-slate-900">{constraintsCount} Active</div>
          </div>
        </div>

        <div
          onClick={() => onNavigateTab('intelligence')}
          className="p-3 bg-white rounded-xl border border-slate-200/90 shadow-2xs cursor-pointer flex items-center gap-3"
        >
          <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
            <Lightbulb className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Opportunities</div>
            <div className="text-sm font-bold text-slate-900">{oppsCount} Identified</div>
          </div>
        </div>

        <div
          onClick={() => onNavigateTab('intelligence')}
          className="p-3 bg-white rounded-xl border border-slate-200/90 shadow-2xs cursor-pointer flex items-center gap-3"
        >
          <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
            <Globe className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">External Factors</div>
            <div className="text-sm font-bold text-slate-900">{externalCount} Monitored</div>
          </div>
        </div>

        <div
          onClick={() => onNavigateTab('options')}
          className="p-3 bg-white rounded-xl border border-slate-200/90 shadow-2xs cursor-pointer flex items-center gap-3"
        >
          <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <Split className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Strategic Options</div>
            <div className="text-sm font-bold text-slate-900">{optionsCount} Evaluated</div>
          </div>
        </div>
      </div>

      {/* Benchmark Variance Chart (When data exists) */}
      {chartData.length > 0 && (
        <div className="p-5 bg-white rounded-2xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Institutional Indicator Benchmarks</h3>
              <p className="text-xs text-slate-500">Observed baseline vs institutional target</p>
            </div>
            <span className="text-xs font-medium text-slate-400">FY {currentPosition?.analysis_period}</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} interval={0} angle={-15} textAnchor="end" />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  formatter={(value: any, name: string) => [
                    `${value}`,
                    name === 'observed' ? 'Observed Baseline' : 'Target Threshold',
                  ]}
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="observed" fill="#2563eb" radius={[4, 4, 0, 0]} barSize={24} name="Observed Baseline" />
                <Bar dataKey="target" fill="#93c5fd" radius={[4, 4, 0, 0]} barSize={24} name="Target Threshold" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Execution Progress Summary if plan exists */}
      {latestReview && (
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Latest Review Status ({latestReview.review_period})
            </div>
            <div className="text-sm font-bold text-slate-900 mt-0.5">
              {latestReview.progress_summary}
            </div>
          </div>
          <StatusBadge status={latestReview.overall_status} />
        </div>
      )}
    </div>
  );
};
