import React from 'react';
import { StrategicOption, Scenario } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { X, ShieldAlert, Sparkles, Layers } from 'lucide-react';

interface OptionDetailModalProps {
  option: StrategicOption | null;
  onClose: () => void;
}

export const OptionDetailModal: React.FC<OptionDetailModalProps> = ({ option, onClose }) => {
  if (!option) return null;

  const scenarios: Scenario[] = option.scenarios || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-start justify-between p-5 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <StatusBadge status={option.priority} size="sm" />
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                Score: {typeof option.total_score === 'number' ? option.total_score.toFixed(1) : 'N/A'} / 100
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900">{option.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          <LeadershipDisclaimer />

          {/* Rationale & Description */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Strategic Rationale & Assessment
            </h4>
            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              {option.strategic_rationale}
            </p>
          </div>

          {/* 7-Dimension Breakdown */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              7-Dimension Multi-Criteria Evaluation
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block text-[10px] uppercase">Strategic Alignment</span>
                <span className="font-bold text-slate-800">{option.strategic_alignment || 'HIGH'}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block text-[10px] uppercase">Impact</span>
                <span className="font-bold text-slate-800">{option.impact || 'HIGH'}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block text-[10px] uppercase">Feasibility</span>
                <span className="font-bold text-slate-800">{option.feasibility || 'MEDIUM'}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block text-[10px] uppercase">Resource Efficiency</span>
                <span className="font-bold text-slate-800">{option.resource_efficiency || 'MEDIUM'}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block text-[10px] uppercase">Risk Profile</span>
                <span className="font-bold text-slate-800">{option.implementation_risk || 'MEDIUM'}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block text-[10px] uppercase">Urgency</span>
                <span className="font-bold text-slate-800">{option.urgency || 'HIGH'}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block text-[10px] uppercase">Evidence Strength</span>
                <span className="font-bold text-slate-800">{option.evidence_strength || 'HIGH'}</span>
              </div>
              <div className="p-2.5 bg-blue-50 rounded-lg border border-blue-200 text-blue-900">
                <span className="text-blue-500 font-semibold block text-[10px] uppercase">Total Evaluated Score</span>
                <span className="font-extrabold text-blue-800 text-sm">
                  {typeof option.total_score === 'number' ? option.total_score.toFixed(1) : 'N/A'} / 100
                </span>
              </div>
            </div>
          </div>

          {/* Conditional Scenarios (Baseline, Upside, Downside, Stress) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Conditional Scenarios ({scenarios.length})
              </h4>
              <span className="text-[11px] text-amber-700 font-medium bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                Conditional scenario — not a prediction.
              </span>
            </div>

            {scenarios.length === 0 ? (
              <div className="text-xs text-slate-500 italic p-4 bg-slate-50 rounded-xl">
                No qualitative scenarios generated for this option.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {scenarios.map((sc, idx) => (
                  <div key={idx} className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900">
                        {sc.scenario_type} SCENARIO
                      </span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                        Qualitative Model
                      </span>
                    </div>

                    {sc.assumptions && sc.assumptions.length > 0 && (
                      <div className="text-xs text-slate-600 space-y-1">
                        <span className="font-semibold text-slate-700 block text-[11px]">Assumptions:</span>
                        {sc.assumptions.map((a, i) => (
                          <div key={i} className="text-[11px] leading-relaxed text-slate-600">• {a}</div>
                        ))}
                      </div>
                    )}

                    {sc.expected_effects && sc.expected_effects.length > 0 && (
                      <div className="text-xs text-slate-600 space-y-1 pt-1 border-t border-slate-100">
                        <span className="font-semibold text-slate-700 block text-[11px]">Expected Effects:</span>
                        {sc.expected_effects.map((e, i) => (
                          <div key={i} className="text-[11px] leading-relaxed text-slate-600">• {e}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs">
          <span className="text-slate-500 italic">
            Status: {option.status}
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-xl shadow-xs transition"
          >
            Close Overview
          </button>
        </div>
      </div>
    </div>
  );
};
