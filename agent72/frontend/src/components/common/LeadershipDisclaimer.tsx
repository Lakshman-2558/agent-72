import React from 'react';
import { ShieldCheck } from 'lucide-react';

interface LeadershipDisclaimerProps {
  customText?: string;
}

export const LeadershipDisclaimer: React.FC<LeadershipDisclaimerProps> = ({ customText }) => {
  return (
    <div className="flex items-start gap-2.5 p-3.5 bg-blue-50/70 border border-blue-200/80 rounded-xl text-blue-900 text-xs">
      <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold">Leadership Decision Support: </span>
        <span>
          {customText ||
            'Agent 72 provides decision-support outputs. Final approval, strategic choices, and resource allocations remain with institutional leadership and governing bodies.'}
        </span>
      </div>
    </div>
  );
};
