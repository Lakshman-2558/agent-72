import React from 'react';
import { Database, CheckCircle2, ShieldCheck, Calendar, Layers } from 'lucide-react';

export interface EvidenceItem {
  evidence_id?: string;
  source_name?: string;
  source_type?: 'AGENT' | 'EXTERNAL' | 'MANUAL' | string;
  source_reference?: string;
  captured_date?: string;
  as_of_date?: string;
  period?: string;
  confidence_score?: number;
  quality_tier?: 'VERIFIED' | 'ESTIMATED' | 'PROVISIONAL' | string;
  findings?: string[];
}

interface EvidencePanelProps {
  evidenceIds?: string[];
  findings?: string[];
  confidence?: number;
  qualityTier?: string;
  evidenceItems?: EvidenceItem[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  evidenceIds = [],
  findings = [],
  confidence,
  qualityTier,
  evidenceItems = [],
}) => {
  if (!evidenceIds.length && !findings.length && confidence === undefined && !evidenceItems.length) {
    return (
      <div className="text-[11px] text-[#6B7F91] italic py-1">
        Insufficient evidence records linked to this indicator.
      </div>
    );
  }

  return (
    <div className="mt-2.5 pt-2.5 border-t border-[#D7E4EE] text-xs text-[#19324A] space-y-2">
      {/* Findings */}
      {findings.length > 0 && (
        <div className="space-y-1">
          {findings.map((f, i) => (
            <div key={i} className="flex items-start gap-1.5 text-[#19324A] text-xs">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#2F6EA6] shrink-0 mt-0.5" />
              <span>{f}</span>
            </div>
          ))}
        </div>
      )}

      {/* Metadata Badges */}
      <div className="flex flex-wrap items-center gap-1.5 pt-0.5 text-[11px] text-[#6B7F91]">
        {confidence !== undefined && (
          <span className="bg-[#E8F4FB] text-[#163A63] border border-[#D7E4EE] px-2 py-0.5 rounded font-semibold">
            Confidence: {Math.round(confidence * 100)}%
          </span>
        )}
        {qualityTier && (
          <span
            className={`px-2 py-0.5 rounded font-semibold border ${
              qualityTier === 'VERIFIED'
                ? 'bg-[#E8F4FB] text-[#16805C] border-[#A7F3D0]'
                : qualityTier === 'ESTIMATED'
                ? 'bg-[#FEF9C3] text-[#B7791F] border-[#FDE68A]'
                : 'bg-[#F5F9FC] text-[#6B7F91] border-[#D7E4EE]'
            }`}
          >
            Tier: {qualityTier}
          </span>
        )}
        {evidenceIds.length > 0 && (
          <span className="flex items-center gap-1 bg-[#F5F9FC] border border-[#D7E4EE] text-[#19324A] px-2 py-0.5 rounded font-mono text-[10.5px]">
            <Database className="w-3 h-3 text-[#2F6EA6]" />
            {evidenceIds.length} {evidenceIds.length === 1 ? 'Evidence ID' : 'Evidence IDs'}
          </span>
        )}
      </div>

      {/* Optional Granular Items */}
      {evidenceItems.length > 0 && (
        <div className="space-y-1.5 pt-1">
          {evidenceItems.slice(0, 3).map((item, idx) => (
            <div
              key={idx}
              className="p-2 bg-[#F5F9FC] border border-[#D7E4EE] rounded-lg text-[11px] space-y-1"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#163A63]">{item.source_name || 'Primary Record'}</span>
                <span className="text-[10px] font-semibold px-1.5 py-0.2 rounded bg-white border border-[#D7E4EE] text-[#2F6EA6]">
                  {item.source_type || 'AGENT'}
                </span>
              </div>
              <div className="flex flex-wrap gap-2 text-[#6B7F91] text-[10px]">
                {item.as_of_date && <span>As-of: {item.as_of_date}</span>}
                {item.period && <span>Period: {item.period}</span>}
                {item.source_reference && <span className="truncate max-w-xs">Ref: {item.source_reference}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

