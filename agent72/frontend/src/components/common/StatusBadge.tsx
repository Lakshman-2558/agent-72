import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const normalized = (status || '').toUpperCase().trim();

  let styleObj = {
    backgroundColor: '#F5F9FC',
    color: '#6B7F91',
    borderColor: '#D7E4EE',
  };

  if (['ON_TRACK', 'IMPROVING', 'ACTIVE', 'APPROVED', 'LOW'].includes(normalized)) {
    styleObj = {
      backgroundColor: '#E8F4FB',
      color: '#16805C',
      borderColor: '#A7F3D0',
    };
  } else if (['AT_RISK', 'VOLATILE', 'PENDING_APPROVAL', 'MEDIUM', 'WARNING'].includes(normalized)) {
    styleObj = {
      backgroundColor: '#FEF9C3',
      color: '#B7791F',
      borderColor: '#FDE68A',
    };
  } else if (['OFF_TRACK', 'DECLINING', 'CRITICAL', 'HIGH', 'DEFICIT'].includes(normalized)) {
    styleObj = {
      backgroundColor: '#FEE2E2',
      color: '#C44B55',
      borderColor: '#FECACA',
    };
  } else if (['INSUFFICIENT_EVIDENCE', 'INSUFFICIENT_DATA', 'UNKNOWN', 'DRAFT', 'STABLE'].includes(normalized)) {
    styleObj = {
      backgroundColor: '#F5F9FC',
      color: '#6B7F91',
      borderColor: '#D7E4EE',
    };
  }

  const label =
    normalized === 'INSUFFICIENT_EVIDENCE' || normalized === 'INSUFFICIENT_DATA'
      ? 'Insufficient Evidence'
      : normalized.replace(/_/g, ' ');

  const sizeClass = size === 'sm' ? 'text-[10.5px] px-2 py-0.5' : 'text-xs font-semibold px-2.5 py-0.5';

  return (
    <span
      style={styleObj}
      className={`inline-flex items-center font-bold tracking-wide rounded-full border shadow-2xs ${sizeClass}`}
    >
      {label}
    </span>
  );
};

