import React, { useState } from 'react';
import { StrategicOptionsAnalysis, StrategicOption } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { EmptyState } from '../common/EmptyState';
import { OptionDetailModal } from './OptionDetailModal';
import { Split, Eye, Layers } from 'lucide-react';

interface StrategicOptionsViewProps {
  analysis?: StrategicOptionsAnalysis | null;
}

export const StrategicOptionsView: React.FC<StrategicOptionsViewProps> = ({ analysis }) => {
  const [selectedOption, setSelectedOption] = useState<StrategicOption | null>(null);

  if (!analysis || !analysis.options?.length) {
    return (
      <EmptyState
        title="No Strategic Options Found"
        description="No strategic alternatives have been evaluated for this institutional period."
      />
    );
  }

  const options = analysis.options;

  return (
    <div className="space-y-6">
      <LeadershipDisclaimer />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-4 bg-white rounded-2xl border border-[#D7E4EE] shadow-2xs">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE]">
              Phase 7 Evaluation
            </span>
            <span className="text-xs text-[#6B7F91]">FY {analysis.analysis_period}</span>
          </div>
          <h2 className="text-base font-bold text-[#163A63]">
            Evaluated Strategic Alternatives ({options.length})
          </h2>
          <p className="text-xs text-[#6B7F91] mt-0.5">
            Ranked by deterministic 7-dimension evaluation score for leadership consideration
          </p>
        </div>
        <span className="text-xs font-bold text-[#163A63] bg-[#E8F4FB] px-3 py-1.5 rounded-xl border border-[#D7E4EE]">
          Decision Support Only
        </span>
      </div>

      {/* Desktop Table View */}
      <div className="hidden md:block overflow-hidden bg-white border border-[#D7E4EE] rounded-2xl shadow-2xs">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-[#D7E4EE] bg-[#F5F9FC] text-[#6B7F91] uppercase font-bold text-[10px] tracking-wider">
              <th className="p-3.5 pl-4">Strategic Option</th>
              <th className="p-3.5">Priority</th>
              <th className="p-3.5">Alignment</th>
              <th className="p-3.5">Impact</th>
              <th className="p-3.5">Feasibility</th>
              <th className="p-3.5">Resource Eff.</th>
              <th className="p-3.5">Risk Profile</th>
              <th className="p-3.5">Score</th>
              <th className="p-3.5 pr-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#D7E4EE]">
            {options.map((opt) => (
              <tr key={opt.id} className="hover:bg-[#F5F9FC] transition">
                <td className="p-3.5 pl-4 font-semibold text-[#19324A] max-w-xs">
                  <div className="font-bold text-[#163A63]">{opt.title}</div>
                  <div className="text-[11px] text-[#6B7F91] font-normal line-clamp-1 mt-0.5">
                    {opt.strategic_rationale}
                  </div>
                </td>
                <td className="p-3.5">
                  <StatusBadge status={opt.priority} size="sm" />
                </td>
                <td className="p-3.5 font-medium text-[#19324A]">{opt.strategic_alignment || 'HIGH'}</td>
                <td className="p-3.5 font-medium text-[#19324A]">{opt.impact || 'HIGH'}</td>
                <td className="p-3.5 font-medium text-[#19324A]">{opt.feasibility || 'MEDIUM'}</td>
                <td className="p-3.5 font-medium text-[#19324A]">{opt.resource_efficiency || 'MEDIUM'}</td>
                <td className="p-3.5 font-medium text-[#19324A]">{opt.implementation_risk || 'MEDIUM'}</td>
                <td className="p-3.5">
                  <span className="font-extrabold text-[#163A63] bg-[#E8F4FB] px-2 py-0.5 rounded border border-[#D7E4EE]">
                    {typeof opt.total_score === 'number' ? opt.total_score.toFixed(0) : 'N/A'}
                  </span>
                </td>
                <td className="p-3.5 pr-4 text-right">
                  <button
                    onClick={() => setSelectedOption(opt)}
                    className="inline-flex items-center gap-1 text-xs font-bold text-[#163A63] hover:text-[#2F6EA6] bg-[#E8F4FB] hover:bg-white px-2.5 py-1 rounded-lg border border-[#D7E4EE] transition shadow-2xs"
                  >
                    <Eye className="w-3.5 h-3.5 text-[#2F6EA6]" />
                    Scenarios
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-3">
        {options.map((opt) => (
          <div key={opt.id} className="p-4 bg-white rounded-xl border border-[#D7E4EE] shadow-2xs space-y-2.5">
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-xs font-bold text-[#163A63]">{opt.title}</h4>
              <StatusBadge status={opt.priority} size="sm" />
            </div>
            <p className="text-xs text-[#6B7F91] line-clamp-2">{opt.strategic_rationale}</p>
            <div className="flex items-center justify-between pt-2 border-t border-[#D7E4EE] text-xs">
              <span className="font-bold text-[#163A63]">
                {typeof opt.total_score === 'number' ? `Score: ${opt.total_score.toFixed(1)}` : 'Score: N/A'}
              </span>
              <button
                onClick={() => setSelectedOption(opt)}
                className="text-xs font-bold text-[#2F6EA6] flex items-center gap-1"
              >
                <Eye className="w-3.5 h-3.5" />
                View Scenarios
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Detail & Scenarios Modal */}
      <OptionDetailModal option={selectedOption} onClose={() => setSelectedOption(null)} />
    </div>
  );
};

