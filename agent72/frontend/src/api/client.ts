import axios from 'axios';
import {
  Institution,
  CurrentPositionAnalysis,
  TrajectoryAnalysis,
  StrategicIntelligenceAnalysis,
  StrategicOptionsAnalysis,
  StrategicPlan,
  ExecutionReview,
  AgentQueryResponse,
} from './types';

const apiBase = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/v1`
  : '/api/v1';

export const apiClient = axios.create({
  baseURL: apiBase,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Organizations
  async getInstitutions(): Promise<Institution[]> {
    const res = await apiClient.get('/organizations/institutions');
    return res.data.items || [];
  },

  // Current Position
  async getCurrentPositions(institutionId?: string, period?: string): Promise<CurrentPositionAnalysis[]> {
    const res = await apiClient.get('/analysis/current-position', {
      params: { institution_id: institutionId, analysis_period: period },
    });
    const items = res.data.items || [];
    return items.map((item: any) => {
      const metrics = (item.key_metrics || item.metric_assessments || []).map((m: any) => ({
        ...m,
        observed_value: m.latest_value ?? m.observed_value ?? null,
        target_value: m.target_value ?? null,
        gap: m.target_variance ?? m.gap ?? null,
        performance_band: m.performance_status ?? m.performance_band ?? 'BASELINE',
        confidence: m.confidence_score ?? m.confidence ?? 0.8,
      }));
      const confScore =
        typeof item.overall_confidence === 'object' && item.overall_confidence !== null
          ? item.overall_confidence.score ?? 0.8
          : typeof item.overall_confidence === 'number'
          ? item.overall_confidence
          : 0.8;
      return {
        ...item,
        title: item.title || `Current Position Analysis (${item.analysis_period})`,
        overall_confidence: confScore,
        metric_assessments: metrics,
        key_metrics: metrics,
      };
    });
  },

  // Trajectory
  async getTrajectories(institutionId?: string, period?: string): Promise<TrajectoryAnalysis[]> {
    const res = await apiClient.get('/analysis/trajectory', {
      params: { institution_id: institutionId, analysis_period: period },
    });
    const items = res.data.items || [];
    return items.map((item: any) => {
      const trends = (item.metric_trends || item.metric_trajectories || []).map((t: any) => ({
        ...t,
        status: t.trend_status ?? t.status ?? 'STABLE',
        net_change: t.absolute_change ?? t.net_change ?? null,
        observation_count: (t.observations ? t.observations.length : t.observation_count) ?? 0,
      }));
      const confScore =
        typeof item.overall_confidence === 'object' && item.overall_confidence !== null
          ? item.overall_confidence.score ?? 0.8
          : typeof item.overall_confidence === 'number'
          ? item.overall_confidence
          : 0.8;
      return {
        ...item,
        title: item.title || `Institutional Trajectory Analysis (${item.analysis_period})`,
        overall_confidence: confScore,
        metric_trajectories: trends,
        metric_trends: trends,
      };
    });
  },

  // Strategic Intelligence
  async getStrategicIntelligence(institutionId?: string, period?: string): Promise<StrategicIntelligenceAnalysis[]> {
    const res = await apiClient.get('/analysis/strategic-intelligence', {
      params: { institution_id: institutionId, analysis_period: period },
    });
    const items = res.data.items || [];
    return items.map((item: any) => {
      const risks = (item.risk_signals || item.risks || []).map((r: any) => ({
        ...r,
        confidence: r.confidence ?? 0.8,
      }));
      const constraints = (item.constraint_signals || item.constraints || []).map((c: any) => ({
        ...c,
        affected_area: c.constraint_type || c.affected_area || 'Operations',
        confidence: c.confidence ?? 0.8,
      }));
      const opportunities = (item.opportunity_signals || item.opportunities || []).map((o: any) => ({
        ...o,
        confidence: o.confidence ?? 0.8,
      }));
      const external = (item.external_factors || []).map((e: any) => ({
        ...e,
        title: e.factor_name || e.title || 'External Factor',
      }));
      const confScore =
        typeof item.overall_confidence === 'object' && item.overall_confidence !== null
          ? item.overall_confidence.score ?? 0.8
          : typeof item.overall_confidence === 'number'
          ? item.overall_confidence
          : 0.8;
      return {
        ...item,
        title: item.title || `Strategic Intelligence Analysis (${item.analysis_period})`,
        overall_confidence: confScore,
        risks,
        risk_signals: risks,
        constraints,
        constraint_signals: constraints,
        opportunities,
        opportunity_signals: opportunities,
        external_factors: external,
      };
    });
  },

  // Strategic Options
  async getStrategicOptions(institutionId?: string, period?: string): Promise<StrategicOptionsAnalysis[]> {
    const res = await apiClient.get('/analysis/strategic-options', {
      params: { institution_id: institutionId, analysis_period: period },
    });
    const items = res.data.items || [];
    return items.map((item: any) => {
      const evalMap = new Map((item.evaluations || []).map((e: any) => [e.option_id, e]));
      const scenMap = new Map<string, any[]>();
      for (const s of item.scenarios || []) {
        if (!scenMap.has(s.option_id)) scenMap.set(s.option_id, []);
        scenMap.get(s.option_id)!.push(s);
      }
      const enrichedOptions = (item.options || []).map((opt: any) => {
        const ev = evalMap.get(opt.id) as any;
        const optScens = scenMap.get(opt.id) || opt.scenarios || [];
        return {
          ...opt,
          evaluation: ev,
          scenarios: optScens,
          total_score: ev?.total_score ?? opt.total_score ?? 0,
          priority: ev?.priority_level ?? opt.priority ?? opt.status ?? 'MEDIUM',
          strategic_alignment: ev ? `${Math.round(ev.strategic_alignment_score)}/20` : opt.strategic_alignment || 'HIGH',
          impact: ev ? `${Math.round(ev.impact_score)}/20` : opt.impact || 'HIGH',
          feasibility: ev ? `${Math.round(ev.feasibility_score)}/15` : opt.feasibility || 'MEDIUM',
          resource_efficiency: ev ? `${Math.round(ev.resource_efficiency_score)}/10` : opt.resource_efficiency || 'MEDIUM',
          implementation_risk: ev ? `${Math.round(ev.implementation_risk_score)}/10` : opt.implementation_risk || 'MEDIUM',
          urgency: ev ? `${Math.round(ev.urgency_score)}/10` : opt.urgency || 'HIGH',
          evidence_strength: ev ? `${Math.round(ev.evidence_strength_score)}/15` : opt.evidence_strength || 'HIGH',
        };
      });
      return {
        ...item,
        title: item.title || `Strategic Options & Scenarios (${item.analysis_period})`,
        options: enrichedOptions,
      };
    });
  },

  // Strategic Plans
  async getPlans(institutionId?: string): Promise<StrategicPlan[]> {
    const res = await apiClient.get('/plans', {
      params: { institution_id: institutionId },
    });
    return res.data.items || [];
  },

  async getPlan(planId: string): Promise<StrategicPlan> {
    const res = await apiClient.get(`/plans/${planId}`);
    return res.data;
  },

  async getLatestExecutionReview(planId: string): Promise<ExecutionReview> {
    const res = await apiClient.get(`/plans/${planId}/review/latest`);
    return res.data;
  },

  // Ask Agent 72
  async askAgent72(institutionId: string, query: string, period?: string): Promise<AgentQueryResponse> {
    const res = await apiClient.post('/analysis/ask', {
      institution_id: institutionId,
      query,
      analysis_period: period,
    });
    return res.data;
  },
};
