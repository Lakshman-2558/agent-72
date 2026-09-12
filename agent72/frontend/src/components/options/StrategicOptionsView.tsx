import React, { useState } from 'react';
import { StrategicOptionsAnalysis, StrategicOption } from '../../api/types';
import { StatusBadge } from '../common/StatusBadge';
import { LeadershipDisclaimer } from '../common/LeadershipDisclaimer';
import { EmptyState } from '../common/EmptyState';
import { OptionDetailModal } from './OptionDetailModal';
import { Split, Eye, AlertCircle } from 'lucide-react';

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

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Split className="w-4 h-4 text-indigo-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Evaluated Strategic Alternatives ({options.length})
          </h3>
        </div>
        <span className="text-xs text-slate-500 font-medium bg-slate-100 px-2.5 py-1 rounded-md">
          Leadership consideration required
        </span>
      </div>

      {/* Desktop Table View */}
      <div className="hidden md:block overflow-hidden bg-white border border-slate-200 rounded-2xl shadow-2xs">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/80 text-slate-500 uppercase font-semibold text-[10px] tracking-wider">
              <th className="p-3.5 pl-4">Strategic Option</th>
              <th className="p-3.5">Priority</th>
              <th className="p-3.5">Alignment</th>
              <th className="p-3.5">Impact</th>
              <th className="p-3.5">Feasibility</th>
              <th className="p-3.5">Risk Profile</th>
              <th className="p-3.5">Urgency</th>
              <th className="p-3.5">Score</th>
              <th className="p-3.5 pr-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {options.map((opt) => (
              <tr key={opt.id} className="hover:bg-slate-50/70 transition">
                <td className="p-3.5 pl-4 font-semibold text-slate-900 max-w-xs">
                  <div>{opt.title}</div>
                  <div className="text-[11px] text-slate-500 font-normal line-clamp-1 mt-0.5">
                    {opt.strategic_rationale}
                  </div>
                </td>
                <td className="p-3.5">
                  <StatusBadge status={opt.priority} size="sm" />
                </td>
                <td className="p-3.5 font-medium text-slate-700">{opt.strategic_alignment || 'HIGH'}</td>
                <td className="p-3.5 font-medium text-slate-700">{opt.impact || 'HIGH'}</td>
                <td className="p-3.5 font-medium text-slate-700">{opt.feasibility || 'MEDIUM'}</td>
                <td className="p-3.5 font-medium text-slate-700">{opt.implementation_risk || 'MEDIUM'}</td>
                <td className="p-3.5 font-medium text-slate-700">{opt.urgency || 'HIGH'}</td>
                <td className="p-3.5">
                  <span className="font-extrabold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    {typeof opt.total_score === 'number' ? opt.total_score.toFixed(0) : 'N/A'}
                  </span>
                </td>
                <td className="p-3.5 pr-4 text-right">
                  <button
                    onClick={() => setSelectedOption(opt)}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2.5 py-1 rounded-lg transition"
                  >
                    <Eye className="w-3.5 h-3.5" />
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
          <div key={opt.id} className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs space-y-2.5">
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-xs font-bold text-slate-900">{opt.title}</h4>
              <StatusBadge status={opt.priority} size="sm" />
            </div>
            <p className="text-xs text-slate-600 line-clamp-2">{opt.strategic_rationale}</p>
            <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
              <span className="font-bold text-blue-700">
                {typeof opt.total_score === 'number' ? `Score: ${opt.total_score.toFixed(1)}` : 'Score: N/A'}
              </span>
              <button
                onClick={() => setSelectedOption(opt)}
                className="text-xs font-semibold text-blue-600 flex items-center gap-1"
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
