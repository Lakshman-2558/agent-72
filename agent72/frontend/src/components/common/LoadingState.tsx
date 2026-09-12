import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading strategic intelligence...',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-slate-500 space-y-3 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
      <Loader2 className="w-7 h-7 text-blue-600 animate-spin" />
      <p className="text-sm font-medium text-slate-600">{message}</p>
    </div>
  );
};
