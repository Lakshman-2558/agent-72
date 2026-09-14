import React from 'react';
import { StrategicOption, Scenario } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { EvidencePanel } from '../common/EvidencePanel';
import { X, ShieldCheck, Layers, ArrowRight } from 'lucide-react';

interface OptionDetailModalProps {
  option: StrategicOption | null;
  onClose: () => void;
}

export const OptionDetailModal: React.FC<OptionDetailModalProps> = ({ option, onClose }) => {
  if (!option) return null;

  const scenarios: Scenario[] = option.scenarios || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#19324A]/50 backdrop-blur-xs">
      <div className="bg-white rounded-2xl border border-[#D7E4EE] shadow-xl max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-start justify-between p-5 border-b border-[#D7E4EE] bg-[#F5F9FC]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
                Decision Support
              </span>
              <StatusBadge status={option.priority} size="sm" />
              <span className="text-xs font-bold text-[#163A63] bg-white px-2 py-0.5 rounded border border-[#D7E4EE]">
                Total Score: {typeof option.total_score === 'number' ? option.total_score.toFixed(1) : 'N/A'} / 100
              </span>
            </div>
            <h3 className="text-base font-bold text-[#163A63]">{option.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-[#6B7F91] hover:text-[#163A63] rounded-lg hover:bg-[#E8F4FB] transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5">
          <LeadershipDisclaimer />

          {/* Rationale & Why it Exists */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              Why this option exists & Strategic Rationale
            </h4>
            <div className="text-xs text-[#19324A] leading-relaxed bg-[#F5F9FC] p-3.5 rounded-xl border border-[#D7E4EE]">
              {option.strategic_rationale}
            </div>
          </div>

          {/* 7-Dimension Evaluation Dimensions */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              7-Dimension Multi-Criteria Evaluation (Deterministic Backend Engine)
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
              <div className="p-2.5 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
                <span className="text-[#6B7F91] font-semibold block text-[10px] uppercase">Strategic Alignment</span>
                <span className="font-bold text-[#19324A]">{option.strategic_alignment || 'HIGH'}</span>
              </div>
              <div className="p-2.5 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
                <span className="text-[#6B7F91] font-semibold block text-[10px] uppercase">Impact</span>
                <span className="font-bold text-[#19324A]">{option.impact || 'HIGH'}</span>
              </div>
              <div className="p-2.5 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
                <span className="text-[#6B7F91] font-semibold block text-[10px] uppercase">Feasibility</span>
                <span className="font-bold text-[#19324A]">{option.feasibility || 'MEDIUM'}</span>
              </div>
              <div className="p-2.5 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
                <span className="text-[#6B7F91] font-semibold block text-[10px] uppercase">Resource Efficiency</span>
                <span className="font-bold text-[#19324A]">{option.resource_efficiency || 'MEDIUM'}</span>
              </div>
              <div className="p-2.5 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
                <span className="text-[#6B7F91] font-semibold block text-[10px] uppercase">Risk Profile</span>
                <span className="font-bold text-[#19324A]">{option.implementation_risk || 'MEDIUM'}</span>
              </div>
              <div className="p-2.5 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
                <span className="text-[#6B7F91] font-semibold block text-[10px] uppercase">Urgency</span>
                <span className="font-bold text-[#19324A]">{option.urgency || 'HIGH'}</span>
              </div>
              <div className="p-2.5 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
                <span className="text-[#6B7F91] font-semibold block text-[10px] uppercase">Evidence Strength</span>
                <span className="font-bold text-[#19324A]">{option.evidence_strength || 'HIGH'}</span>
              </div>
              <div className="p-2.5 bg-[#E8F4FB] rounded-xl border border-[#D7E4EE]">
                <span className="text-[#2F6EA6] font-semibold block text-[10px] uppercase">Total Evaluated Score</span>
                <span className="font-extrabold text-[#163A63] text-sm">
                  {typeof option.total_score === 'number' ? option.total_score.toFixed(1) : 'N/A'} / 100
                </span>
              </div>
            </div>
          </div>

          {/* Conditional Scenarios (Baseline, Upside, Downside, Stress) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
                Conditional Qualitative Scenarios ({scenarios.length})
              </h4>
              <span className="text-[10.5px] font-bold px-2 py-0.5 rounded bg-[#E8F4FB] text-[#2F6EA6] border border-[#D7E4EE]">
                Decision support — conditional projections, not guaranteed predictions
              </span>
            </div>

            {scenarios.length === 0 ? (
              <div className="text-xs text-[#6B7F91] italic p-4 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE]">
                No conditional scenarios formulated for this option.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {scenarios.map((sc, idx) => (
                  <div key={idx} className="p-4 bg-[#F5F9FC] rounded-xl border border-[#D7E4EE] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#163A63]">
                        {sc.scenario_type} SCENARIO
                      </span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-white text-[#6B7F91] border border-[#D7E4EE]">
                        Qualitative Projection
                      </span>
                    </div>

                    {sc.assumptions && sc.assumptions.length > 0 && (
                      <div className="text-xs text-[#19324A] space-y-0.5">
                        <span className="font-semibold text-[#6B7F91] block text-[10.5px]">Assumptions:</span>
                        {sc.assumptions.map((a, i) => (
                          <div key={i} className="text-[11px] leading-relaxed text-[#19324A]">• {a}</div>
                        ))}
                      </div>
                    )}

                    {sc.expected_effects && sc.expected_effects.length > 0 && (
                      <div className="text-xs text-[#19324A] space-y-0.5 pt-1 border-t border-[#D7E4EE]">
                        <span className="font-semibold text-[#6B7F91] block text-[10.5px]">Expected Effects:</span>
                        {sc.expected_effects.map((e, i) => (
                          <div key={i} className="text-[11px] leading-relaxed text-[#19324A]">• {e}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Evidence Traceability */}
          <div className="space-y-1 pt-1">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#163A63]">
              Supporting Evidence
            </h4>
            <EvidencePanel evidenceIds={option.evidence_ids} />
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-[#D7E4EE] bg-[#F5F9FC] flex items-center justify-between text-xs">
          <span className="text-[#6B7F91] font-semibold">
            Status: {option.status} (Governed by Leadership)
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-[#163A63] hover:bg-[#2F6EA6] text-white font-bold rounded-xl shadow-2xs transition"
          >
            Close Overview
          </button>
        </div>
      </div>
    </div>
  );
};

