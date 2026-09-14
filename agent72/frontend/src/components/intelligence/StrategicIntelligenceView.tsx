import React, { useState } from 'react';
import {
  StrategicIntelligenceAnalysis,
  StrategicRisk,
  StrategicConstraint,
  StrategicOpportunity,
  ExternalFactor,
} from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { EmptyState } from '../common/EmptyState';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { EvidencePanel } from '../common/EvidencePanel';
import {
  AlertTriangle,
  Lock,
  Lightbulb,
  Globe,
  ChevronDown,
  ChevronUp,
  Brain,
  ListOrdered,
  Layers,
  Database,
  Search,
} from 'lucide-react';

interface StrategicIntelligenceViewProps {
  analysis?: StrategicIntelligenceAnalysis | null;
}

export const StrategicIntelligenceView: React.FC<StrategicIntelligenceViewProps> = ({ analysis }) => {
  const [expandedCardId, setExpandedCardId] = useState<string | null>(null);
  const [filterQuery, setFilterQuery] = useState('');

  if (!analysis) {
    return (
      <EmptyState
        title="No Strategic Intelligence Found"
        description="No strategic intelligence synthesis has been generated for this institutional period."
      />
    );
  }

  const toggleExpand = (id: string) => {
    setExpandedCardId((prev) => (prev === id ? null : id));
  };

  const strategicIssues = analysis.strategic_issues || [];
  const risks = analysis.risk_signals || analysis.risks || [];
  const constraints = analysis.constraint_signals || analysis.constraints || [];
  const opportunities = analysis.opportunity_signals || analysis.opportunities || [];
  const externalFactors = analysis.external_factors || [];
  const prioritySignals = (analysis as any).strategic_priority_signals || [];

  return (
    <div className="space-y-6">
      <LeadershipDisclaimer />

      {/* View Header & Meta */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 bg-white rounded-2xl border border-[#D7E4EE] shadow-2xs">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
              Phase 6 Synthesis
            </span>
            <span className="text-xs text-[#6B7F91]">FY {analysis.analysis_period}</span>
          </div>
          <h2 className="text-base font-bold text-[#163A63]">
            Institutional Strategic Intelligence
          </h2>
          <p className="text-xs text-[#6B7F91] mt-0.5">
            Cross-metric risks, institutional constraints, external market factors, and priority signals
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-center">
          <span className="text-xs font-bold px-3 py-1.5 bg-[#E8F4FB] text-[#163A63] rounded-xl border border-[#D7E4EE]">
            Overall Confidence: {Math.round((analysis.overall_confidence ?? 0.8) * 100)}%
          </span>
        </div>
      </div>

      {/* Observation vs Interpretation Methodology Notice */}
      <div className="p-3.5 bg-[#E8F4FB] border border-[#D7E4EE] rounded-xl text-xs text-[#19324A] flex items-start gap-2.5">
        <Brain className="w-4 h-4 text-[#2F6EA6] shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <span className="font-bold text-[#163A63]">Methodological Governance: </span>
          <span>
            Agent 72 strictly separates <strong>OBSERVATION</strong> (verified baseline metrics and time-series evidence) from <strong>STRATEGIC INTERPRETATION</strong> (contextual risk synthesis, operational constraints, and multi-factor scenarios). No causal claims are asserted without empirical evidence.
          </span>
        </div>
      </div>

      {/* 1. Strategic Priority Signals */}
      {prioritySignals.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <ListOrdered className="w-4 h-4 text-[#2F6EA6]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              Priority Strategic Signals ({prioritySignals.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {prioritySignals.map((ps: any, idx: number) => (
              <div
                key={ps.id || idx}
                className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs space-y-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-bold text-[#19324A]">{ps.title}</h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
                    Score: {ps.priority_score?.toFixed(1) ?? 'N/A'}
                  </span>
                </div>
                <p className="text-xs text-[#6B7F91] leading-relaxed">{ps.rationale}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 2. Strategic Issues */}
      {strategicIssues.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#163A63]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              Strategic Issues ({strategicIssues.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {strategicIssues.map((issue: any, idx: number) => (
              <div
                key={issue.id || idx}
                className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs space-y-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-bold text-[#19324A]">{issue.title}</h4>
                  <StatusBadge status={issue.severity || 'MEDIUM'} size="sm" />
                </div>
                <p className="text-xs text-[#6B7F91] leading-relaxed">{issue.description}</p>
                {issue.rationale && (
                  <p className="text-[11px] text-[#2F6EA6] italic pt-1 border-t border-[#D7E4EE]">
                    Rationale: {issue.rationale}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Strategic Risks */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-[#C44B55]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
            Strategic Risks ({risks.length})
          </h3>
        </div>

        {risks.length === 0 ? (
          <div className="p-4 bg-white rounded-xl border border-[#D7E4EE] text-xs text-[#6B7F91] italic">
            No active strategic risks detected for this period.
          </div>
        ) : (
          <div className="space-y-2.5">
            {risks.map((r: any, i: number) => {
              const cardId = `risk-${i}`;
              const isExpanded = expandedCardId === cardId;
              return (
                <div
                  key={cardId}
                  className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs hover:border-[#2F6EA6] transition"
                >
                  <div
                    className="flex items-start justify-between gap-3 cursor-pointer"
                    onClick={() => toggleExpand(cardId)}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <StatusBadge status={r.severity || 'HIGH'} size="sm" />
                        <h4 className="text-xs font-bold text-[#19324A]">{r.title}</h4>
                      </div>
                      <p className="text-xs text-[#6B7F91] mt-1.5 leading-relaxed">{r.description}</p>
                    </div>
                    <button className="text-[#6B7F91] hover:text-[#163A63] p-1">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* Observable vs Interpretation Evidence Drilldown */}
                  {isExpanded && (
                    <div className="mt-3 pt-3 border-t border-[#D7E4EE] bg-[#F5F9FC] -mx-4 -mb-4 p-4 rounded-b-xl space-y-2.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[#163A63] uppercase text-[11px] tracking-wider">
                          Why did Agent 72 identify this?
                        </span>
                        <span className="text-[10.5px] font-semibold text-[#6B7F91]">
                          Confidence: {Math.round((r.confidence ?? 0.8) * 100)}%
                        </span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-[11px]">
                        <div>
                          <span className="text-[#6B7F91] font-semibold block uppercase text-[10px]">Severity</span>
                          <span className="font-bold text-[#19324A]">{r.severity}</span>
                        </div>
                        <div>
                          <span className="text-[#6B7F91] font-semibold block uppercase text-[10px]">Impact</span>
                          <span className="font-bold text-[#19324A]">{r.impact || 'STRUCTURAL'}</span>
                        </div>
                        <div>
                          <span className="text-[#6B7F91] font-semibold block uppercase text-[10px]">Likelihood</span>
                          <span className="font-bold text-[#19324A]">{r.likelihood || 'EVALUATED'}</span>
                        </div>
                        <div>
                          <span className="text-[#6B7F91] font-semibold block uppercase text-[10px]">Risk Score</span>
                          <span className="font-bold text-[#163A63]">{r.risk_score?.toFixed(1) ?? 'N/A'}</span>
                        </div>
                      </div>

                      {/* Observations vs Interpretation */}
                      <div className="p-2.5 bg-white border border-[#D7E4EE] rounded-lg space-y-1 text-[11px]">
                        <div className="font-bold text-[#163A63]">Observation vs Interpretation:</div>
                        <p className="text-[#6B7F91]">
                          <strong>Observation: </strong>
                          {r.supporting_indicators && r.supporting_indicators.length > 0
                            ? r.supporting_indicators.join('; ')
                            : 'Derived from multi-period time-series indicators.'}
                        </p>
                        {r.correlation_vs_causation_note && (
                          <p className="text-[#6B7F91]">
                            <strong>Causality Boundary: </strong>
                            {r.correlation_vs_causation_note}
                          </p>
                        )}
                      </div>

                      {r.related_metrics && r.related_metrics.length > 0 && (
                        <div className="text-[11px]">
                          <span className="text-[#6B7F91] font-medium">Related Canonical Metrics: </span>
                          <span className="font-mono text-[#2F6EA6] font-semibold">
                            {r.related_metrics.join(', ')}
                          </span>
                        </div>
                      )}

                      <EvidencePanel
                        evidenceIds={r.evidence_ids || r.evidence_references}
                        confidence={r.confidence}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 4. Institutional Constraints */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Lock className="w-4 h-4 text-[#B7791F]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
            Institutional Constraints ({constraints.length})
          </h3>
        </div>

        {constraints.length === 0 ? (
          <div className="p-4 bg-white rounded-xl border border-[#D7E4EE] text-xs text-[#6B7F91] italic">
            No binding physical or operational constraints flagged.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {constraints.map((c: any, idx: number) => (
              <div key={idx} className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs space-y-2">
                <div className="flex items-start justify-between">
                  <h4 className="text-xs font-bold text-[#19324A]">{c.title}</h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#FEF9C3] text-[#B7791F] border border-[#FDE68A]">
                    {c.affected_area || c.constraint_type || 'Operations'}
                  </span>
                </div>
                {c.description && <p className="text-xs text-[#6B7F91]">{c.description}</p>}
                {c.rationale && (
                  <p className="text-[11px] text-[#19324A] pt-1 border-t border-[#D7E4EE]">
                    <strong>Rationale: </strong>{c.rationale}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 5. Strategic Opportunities */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-[#16805C]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
            Strategic Opportunities ({opportunities.length})
          </h3>
        </div>

        {opportunities.length === 0 ? (
          <div className="p-4 bg-white rounded-xl border border-[#D7E4EE] text-xs text-[#6B7F91] italic">
            No emergent strategic opportunities identified from current baseline evidence.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {opportunities.map((o: any, idx: number) => (
              <div key={idx} className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs space-y-2">
                <div className="flex items-start justify-between">
                  <h4 className="text-xs font-bold text-[#19324A]">{o.title}</h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#E8F4FB] text-[#16805C] border border-[#A7F3D0]">
                    {Math.round((o.confidence ?? 0.8) * 100)}% Confidence
                  </span>
                </div>
                {o.description && <p className="text-xs text-[#6B7F91]">{o.description}</p>}
                {o.rationale && (
                  <p className="text-[11px] text-[#19324A] pt-1 border-t border-[#D7E4EE]">
                    <strong>Rationale: </strong>{o.rationale}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 6. External Factors */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-[#2F6EA6]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
            External Environmental Factors ({externalFactors.length})
          </h3>
        </div>

        {externalFactors.length === 0 ? (
          <div className="p-4 bg-white rounded-xl border border-[#D7E4EE] text-xs text-[#6B7F91] italic">
            No external market or regulatory signals recorded.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {externalFactors.map((e: any, idx: number) => (
              <div key={idx} className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs space-y-2">
                <div className="flex items-start justify-between">
                  <h4 className="text-xs font-bold text-[#19324A]">{e.title || e.factor_name}</h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
                    {e.category}
                  </span>
                </div>
                {e.description && <p className="text-xs text-[#6B7F91]">{e.description}</p>}
                {e.rationale && (
                  <p className="text-[11px] text-[#19324A] pt-1 border-t border-[#D7E4EE]">
                    <strong>Rationale: </strong>{e.rationale}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

