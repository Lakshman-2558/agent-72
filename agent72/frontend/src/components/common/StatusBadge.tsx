import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const normalized = (status || '').toUpperCase().trim();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';

  if (['ON_TRACK', 'IMPROVING', 'ACTIVE', 'APPROVED', 'LOW'].includes(normalized)) {
    colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (['AT_RISK', 'VOLATILE', 'PENDING_APPROVAL', 'MEDIUM', 'WARNING'].includes(normalized)) {
    colorClasses = 'bg-amber-50 text-amber-700 border-amber-200';
  } else if (['OFF_TRACK', 'DECLINING', 'CRITICAL', 'HIGH', 'DEFICIT'].includes(normalized)) {
    colorClasses = 'bg-rose-50 text-rose-700 border-rose-200';
  } else if (['INSUFFICIENT_EVIDENCE', 'INSUFFICIENT_DATA', 'UNKNOWN', 'DRAFT', 'STABLE'].includes(normalized)) {
    colorClasses = 'bg-slate-100 text-slate-700 border-slate-300';
  }

  const label = normalized === 'INSUFFICIENT_EVIDENCE'
    ? 'Insufficient Evidence'
    : normalized.replace(/_/g, ' ');

  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-xs font-semibold px-2.5 py-1';

  return (
    <span className={`inline-flex items-center rounded-full border ${sizeClass} ${colorClasses}`}>
      {label}
    </span>
  );
};
