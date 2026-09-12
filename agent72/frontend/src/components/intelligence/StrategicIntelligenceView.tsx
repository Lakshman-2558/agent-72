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
import {
  AlertTriangle,
  Lock,
  Lightbulb,
  Globe,
  ChevronDown,
  ChevronUp,
  Info,
} from 'lucide-react';

interface StrategicIntelligenceViewProps {
  analysis?: StrategicIntelligenceAnalysis | null;
}

export const StrategicIntelligenceView: React.FC<StrategicIntelligenceViewProps> = ({ analysis }) => {
  const [expandedCardId, setExpandedCardId] = useState<string | null>(null);

  if (!analysis) {
    return (
      <EmptyState
        title="No Strategic Intelligence Found"
        description="No strategic intelligence synthesis has been generated for this period."
      />
    );
  }

  const toggleExpand = (id: string) => {
    setExpandedCardId((prev) => (prev === id ? null : id));
  };

  const risks = analysis.risks || [];
  const constraints = analysis.constraints || [];
  const opportunities = analysis.opportunities || [];
  const externalFactors = analysis.external_factors || [];

  return (
    <div className="space-y-6">
      {/* 1. Strategic Risks */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Strategic Risks ({risks.length})
          </h3>
        </div>

        {risks.length === 0 ? (
          <div className="p-4 bg-white rounded-xl border border-slate-200 text-xs text-slate-500 italic">
            No active strategic risks detected for this period.
          </div>
        ) : (
          <div className="space-y-2.5">
            {risks.map((r, i) => {
              const cardId = `risk-${i}`;
              const isExpanded = expandedCardId === cardId;
              return (
                <div
                  key={cardId}
                  className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs hover:border-slate-300 transition"
                >
                  <div className="flex items-start justify-between gap-3 cursor-pointer" onClick={() => toggleExpand(cardId)}>
                    <div>
                      <div className="flex items-center gap-2">
                        <StatusBadge status={r.severity} size="sm" />
                        <h4 className="text-xs font-bold text-slate-900">{r.title}</h4>
                      </div>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{r.description}</p>
                    </div>
                    <button className="text-slate-400 hover:text-slate-600">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* "Why did Agent 72 identify this?" Drilldown */}
                  {isExpanded && (
                    <div className="mt-3 pt-3 border-t border-slate-100 bg-slate-50/70 -mx-4 -mb-4 p-4 rounded-b-xl space-y-2 text-xs">
                      <div className="flex items-center gap-1.5 font-bold text-blue-900">
                        <Info className="w-3.5 h-3.5 text-blue-600" />
                        <span>Why did Agent 72 identify this?</span>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-[11px]">
                        <div>
                          <span className="text-slate-400 font-semibold block uppercase">Severity</span>
                          <span className="font-bold text-slate-800">{r.severity}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 font-semibold block uppercase">Confidence</span>
                          <span className="font-bold text-slate-800">{Math.round((r.confidence || 0.8) * 100)}%</span>
                        </div>
                        <div>
                          <span className="text-slate-400 font-semibold block uppercase">Likelihood</span>
                          <span className="font-bold text-slate-800">{r.likelihood || 'EVALUATED'}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 font-semibold block uppercase">Impact</span>
                          <span className="font-bold text-slate-800">{r.impact || 'STRUCTURAL'}</span>
                        </div>
                      </div>

                      {r.related_metric_keys && r.related_metric_keys.length > 0 && (
                        <div className="pt-1">
                          <span className="text-slate-500 font-medium">Related Canonical Metrics: </span>
                          <span className="font-mono text-[11px] text-blue-700">
                            {r.related_metric_keys.join(', ')}
                          </span>
                        </div>
                      )}

                      {r.evidence_references && r.evidence_references.length > 0 && (
                        <div className="pt-1 text-slate-500">
                          <span className="font-medium">Evidence References: </span>
                          <span>{r.evidence_references.join('; ')}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 2. Institutional Constraints */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Lock className="w-4 h-4 text-amber-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Institutional Constraints ({constraints.length})
          </h3>
        </div>

        {constraints.length === 0 ? (
          <div className="p-4 bg-white rounded-xl border border-slate-200 text-xs text-slate-500 italic">
            No binding physical or operational constraints flagged.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {constraints.map((c, idx) => (
              <div key={idx} className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs space-y-2">
                <div className="flex items-start justify-between">
                  <h4 className="text-xs font-bold text-slate-900">{c.title}</h4>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                    {c.affected_area}
                  </span>
                </div>
                {c.description && <p className="text-xs text-slate-600">{c.description}</p>}
                {c.uncertainty && (
                  <div className="text-[11px] text-slate-500 italic">
                    Uncertainty: {c.uncertainty}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Strategic Opportunities */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-emerald-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Strategic Opportunities ({opportunities.length})
          </h3>
        </div>

        {opportunities.length === 0 ? (
          <div className="p-4 bg-white rounded-xl border border-slate-200 text-xs text-slate-500 italic">
            No emergent strategic opportunities identified from current baseline evidence.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {opportunities.map((o, idx) => (
              <div key={idx} className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs space-y-2">
                <div className="flex items-start justify-between">
                  <h4 className="text-xs font-bold text-slate-900">{o.title}</h4>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                    {Math.round((o.confidence || 0.8) * 100)}% Confidence
                  </span>
                </div>
                {o.description && <p className="text-xs text-slate-600">{o.description}</p>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 4. External Factors */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-blue-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            External Environmental Factors ({externalFactors.length})
          </h3>
        </div>

        {externalFactors.length === 0 ? (
          <div className="p-4 bg-white rounded-xl border border-slate-200 text-xs text-slate-500 italic">
            No external market or regulatory signals recorded.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {externalFactors.map((e, idx) => (
              <div key={idx} className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs space-y-2">
                <div className="flex items-start justify-between">
                  <h4 className="text-xs font-bold text-slate-900">{e.title}</h4>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200">
                    {e.category}
                  </span>
                </div>
                {e.description && <p className="text-xs text-slate-600">{e.description}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
