import React from 'react';

export const RobotConstellationStage: React.FC = () => {
  return (
    <div className="relative w-full h-64 sm:h-72 rounded-2xl bg-gradient-to-b from-[#e0f2fe] via-[#dbeafe] to-[#bfdbfe] border border-blue-200/80 shadow-xs overflow-hidden flex items-center justify-center select-none">
      {/* Constellation / Network Background SVG */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none opacity-45"
        viewBox="0 0 700 300"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Network Connecting Lines */}
        <line x1="80" y1="60" x2="160" y2="120" stroke="#60a5fa" strokeWidth="1" strokeDasharray="3 3" />
        <line x1="160" y1="120" x2="110" y2="200" stroke="#60a5fa" strokeWidth="1" />
        <line x1="160" y1="120" x2="260" y2="80" stroke="#60a5fa" strokeWidth="1" />
        <line x1="260" y1="80" x2="220" y2="170" stroke="#60a5fa" strokeWidth="1" strokeDasharray="4 4" />

        <line x1="480" y1="70" x2="560" y2="130" stroke="#60a5fa" strokeWidth="1" />
        <line x1="560" y1="130" x2="630" y2="90" stroke="#60a5fa" strokeWidth="1" strokeDasharray="3 3" />
        <line x1="560" y1="130" x2="520" y2="220" stroke="#60a5fa" strokeWidth="1" />
        <line x1="630" y1="90" x2="660" y2="180" stroke="#60a5fa" strokeWidth="1" />
        <line x1="480" y1="70" x2="430" y2="140" stroke="#60a5fa" strokeWidth="1" strokeDasharray="3 3" />

        {/* Constellation Nodes */}
        <circle cx="80" cy="60" r="3" fill="#3b82f6" />
        <circle cx="160" cy="120" r="4" fill="#2563eb" />
        <circle cx="110" cy="200" r="3" fill="#60a5fa" />
        <circle cx="260" cy="80" r="3.5" fill="#3b82f6" />
        <circle cx="220" cy="170" r="3" fill="#93c5fd" />

        <circle cx="480" cy="70" r="3.5" fill="#3b82f6" />
        <circle cx="560" cy="130" r="4.5" fill="#1d4ed8" />
        <circle cx="630" cy="90" r="3" fill="#60a5fa" />
        <circle cx="520" cy="220" r="3" fill="#93c5fd" />
        <circle cx="660" cy="180" r="3.5" fill="#3b82f6" />
        <circle cx="430" cy="140" r="2.5" fill="#93c5fd" />
      </svg>

      {/* Floating Center Glow */}
      <div className="absolute w-52 h-52 bg-white/40 rounded-full blur-2xl pointer-events-none" />

      {/* Robot Character standing and gently floating */}
      <div className="relative z-10 flex flex-col items-center justify-center">
        <img
          src="/agent72-robot.png"
          alt="Agent 72 - Institutional Strategic Planning Assistant"
          className="w-40 h-40 sm:w-48 sm:h-48 object-contain animate-float drop-shadow-lg"
        />
      </div>
    </div>
  );
};
