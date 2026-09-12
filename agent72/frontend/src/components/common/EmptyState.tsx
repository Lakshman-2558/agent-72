import React from 'react';
import { FileQuestion } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionButton?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No strategic intelligence available',
  description = 'No evidence or analytical snapshots found for this institutional period.',
  actionButton,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center text-slate-500 space-y-3 bg-white border border-dashed border-slate-300 rounded-2xl">
      <div className="p-3 bg-slate-100 text-slate-500 rounded-full">
        <FileQuestion className="w-6 h-6" />
      </div>
      <div className="space-y-1">
        <h4 className="text-sm font-semibold text-slate-800">{title}</h4>
        <p className="text-xs text-slate-500 max-w-sm">{description}</p>
      </div>
      {actionButton && <div className="pt-2">{actionButton}</div>}
    </div>
  );
};
