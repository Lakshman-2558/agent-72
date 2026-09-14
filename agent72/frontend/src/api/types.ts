/**
 * TypeScript Data Models matching Agent 72 Backend DTOs
 */

export interface Institution {
  id: string;
  code: string;
  name: string;
  institution_type?: string;
  jurisdiction?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface MetricAssessment {
  metric_key: string;
  metric_name?: string;
  domain?: string;
  observed_value?: number | null;
  target_value?: number | null;
  baseline_value?: number | null;
  unit?: string;
  gap?: number | null;
  gap_unit_label?: string | null;
  performance_band?: string;
  confidence?: number;
  data_quality_tier?: string;
  evidence_count?: number;
  evidence_ids?: string[];
  findings?: string[];
}

export interface CurrentPositionAnalysis {
  id: string;
  institution_id: string;
  analysis_period: string;
  title: string;
  overall_confidence: number;
  metric_assessments: MetricAssessment[];
  key_metrics?: MetricAssessment[];
  strengths: any[];
  gaps: any[];
  opportunities: any[];
  data_gaps: any[];
  created_at: string;
}

export interface MetricTrajectory {
  metric_key: string;
  metric_name?: string;
  status: 'IMPROVING' | 'STABLE' | 'DECLINING' | 'VOLATILE' | 'INSUFFICIENT_DATA';
  net_change?: number | null;
  unit?: string;
  observation_count: number;
  consistency_score?: number;
  direction?: string;
  historical_points?: { period: string; value: number }[];
  findings?: string[];
}

export interface TrajectoryAnalysis {
  id: string;
  institution_id: string;
  analysis_period: string;
  title: string;
  overall_confidence: number;
  metric_trajectories: MetricTrajectory[];
  metric_trends?: MetricTrajectory[];
  created_at: string;
}

export interface StrategicRisk {
  id?: string;
  title: string;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  likelihood?: string;
  impact?: string;
  confidence: number;
  evidence_references?: string[];
  related_metric_keys?: string[];
  assumptions?: string[];
  uncertainty?: string;
}

export interface StrategicConstraint {
  id?: string;
  title: string;
  affected_area: string;
  description?: string;
  evidence_references?: string[];
  uncertainty?: string;
  confidence?: number;
}

export interface StrategicOpportunity {
  id?: string;
  title: string;
  description?: string;
  confidence: number;
  evidence_references?: string[];
  related_metric_keys?: string[];
}

export interface ExternalFactor {
  id?: string;
  title: string;
  category: 'REGULATORY' | 'MARKET' | 'EMPLOYER_DEMAND' | 'COMPETITOR' | 'DEMOGRAPHIC' | string;
  description?: string;
  impact?: string;
  evidence_references?: string[];
}

export interface StrategicIntelligenceAnalysis {
  id: string;
  institution_id: string;
  analysis_period: string;
  overall_confidence: number;
  strategic_issues?: any[];
  risks: StrategicRisk[];
  constraints: StrategicConstraint[];
  opportunities: StrategicOpportunity[];
  external_factors: ExternalFactor[];
  risk_signals?: StrategicRisk[];
  constraint_signals?: StrategicConstraint[];
  opportunity_signals?: StrategicOpportunity[];
  created_at: string;
}

export interface Scenario {
  scenario_type: 'BASELINE' | 'UPSIDE' | 'DOWNSIDE' | 'STRESS';
  title?: string;
  assumptions: string[];
  expected_effects: string[];
  risks?: string[];
  opportunities?: string[];
  uncertainty?: string;
}

export interface StrategicOption {
  id: string;
  title: string;
  category?: string;
  description?: string;
  strategic_rationale: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  strategic_alignment?: string;
  impact?: string;
  feasibility?: string;
  resource_efficiency?: string;
  resource_intensity?: string;
  implementation_risk?: string;
  urgency?: string;
  evidence_strength?: string;
  total_score: number;
  status: 'CANDIDATE' | 'SELECTED_FOR_PLANNING' | 'IN_PLAN' | 'DEFERRED' | 'REJECTED';
  scenarios: Scenario[];
  evidence_ids?: string[];
  dependencies?: string[];
}

export interface StrategicOptionsAnalysis {
  id: string;
  institution_id: string;
  analysis_period: string;
  options: StrategicOption[];
  prioritized_option_ids?: string[];
  scenarios?: any[];
  evaluations?: any[];
  created_at: string;
}

export interface InitiativeMilestone {
  id: string;
  title: string;
  description?: string;
  due_period?: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'DELAYED' | string;
  completion_percentage?: number;
}

export interface PlanInitiative {
  id: string;
  title: string;
  description?: string;
  rationale?: string;
  owner_unit_id?: string;
  unit_owner?: string;
  supporting_units?: string[];
  resource_requirement?: 'LOW' | 'MEDIUM' | 'HIGH' | 'UNKNOWN' | string;
  implementation_risk?: string;
  start_period?: string;
  end_period?: string;
  status: string;
  milestones: InitiativeMilestone[];
}

export interface StrategicTarget {
  id: string;
  metric_key: string;
  baseline_value?: number | null;
  baseline_period?: string | null;
  target_value?: number | null;
  target_period?: string | null;
  direction?: string;
  unit?: string;
  gap?: number | null;
  gap_unit_label?: string | null;
  status?: string;
  confidence?: number;
  target_provenance?: string;
  evidence_ids?: string[];
}

export interface StrategicObjective {
  id: string;
  title: string;
  description?: string;
  strategic_rationale?: string;
  owner_unit_id?: string;
  owner?: string;
  status?: string;
  priority?: string;
  targets: StrategicTarget[];
  initiatives: PlanInitiative[];
}

export interface TargetVariance {
  metric_key: string;
  baseline_value?: number | null;
  target_value?: number | null;
  observed_value?: number | null;
  observed_period?: string | null;
  absolute_variance?: number | null;
  unit?: string;
  is_percentage?: boolean;
  variance_notation: string;
  direction?: string;
  status: 'ON_TRACK' | 'AT_RISK' | 'OFF_TRACK' | 'INSUFFICIENT_EVIDENCE';
  notes?: string;
}

export interface CorrectiveActionCandidate {
  id: string;
  signal_type: string;
  title: string;
  description: string;
  suggested_action: string;
  rationale: string;
  requires_leadership_approval: boolean;
}

export interface ExecutionReview {
  id: string;
  strategic_plan_id: string;
  review_period: string;
  review_date: string;
  overall_status: 'ON_TRACK' | 'AT_RISK' | 'OFF_TRACK' | 'INSUFFICIENT_EVIDENCE';
  progress_summary: string;
  metric_variances: TargetVariance[];
  diagnostic_signals: string[];
  corrective_actions: CorrectiveActionCandidate[];
  leadership_disclaimer?: string;
  created_at: string;
}

export interface StrategicPlan {
  id: string;
  institution_id: string;
  institution_name?: string;
  title: string;
  horizon_start_year: number;
  horizon_end_year: number;
  status: 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'ACTIVE' | 'UNDER_REVIEW' | 'ARCHIVED';
  objectives: StrategicObjective[];
  execution_reviews?: ExecutionReview[];
  leadership_disclaimer?: string;
  created_at: string;
}

export interface AgentQueryResponse {
  answer: string;
  confidence: number;
  grounding_sources: any[];
  related_metrics: string[];
  suggested_questions: string[];
  leadership_disclaimer: string;
}
