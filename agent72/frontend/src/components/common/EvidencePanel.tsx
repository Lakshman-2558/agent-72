import React from 'react';
import { Database, CheckCircle2 } from 'lucide-react';

interface EvidencePanelProps {
  evidenceIds?: string[];
  findings?: string[];
  confidence?: number;
  qualityTier?: string;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  evidenceIds = [],
  findings = [],
  confidence,
  qualityTier,
}) => {
  if (!evidenceIds.length && !findings.length && confidence === undefined) {
    return (
      <div className="text-xs text-slate-500 italic py-1">
        Insufficient evidence records linked to this indicator.
      </div>
    );
  }

  return (
    <div className="mt-2.5 pt-2.5 border-t border-slate-100 text-xs text-slate-600 space-y-1.5">
      {findings.length > 0 && (
        <div className="space-y-1">
          {findings.map((f, i) => (
            <div key={i} className="flex items-start gap-1.5 text-slate-700">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-500 shrink-0 mt-0.5" />
              <span>{f}</span>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-500">
        {confidence !== undefined && (
          <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">
            Confidence: {Math.round(confidence * 100)}%
          </span>
        )}
        {qualityTier && (
          <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-medium">
            Quality: {qualityTier}
          </span>
        )}
        {evidenceIds.length > 0 && (
          <span className="flex items-center gap-1 bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
            <Database className="w-3 h-3 text-slate-400" />
            {evidenceIds.length} Evidence {evidenceIds.length === 1 ? 'Record' : 'Records'}
          </span>
        )}
      </div>
    </div>
  );
};
