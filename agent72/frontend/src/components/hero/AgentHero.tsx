import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowRight } from 'lucide-react';
import agent72Robot from '../../assets/agent72-robot.png';

export const AgentHero: React.FC = () => {
  // Dynamic typewriter effect for "72" in main heading
  const [typedNum, setTypedNum] = useState('72');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const fullText = '72';
    let timeout: ReturnType<typeof setTimeout>;

    if (!isDeleting) {
      if (typedNum.length < fullText.length) {
        timeout = setTimeout(() => {
          setTypedNum(fullText.slice(0, typedNum.length + 1));
        }, 280);
      } else {
        // Pause when fully typed
        timeout = setTimeout(() => {
          setIsDeleting(true);
        }, 2400);
      }
    } else {
      if (typedNum.length > 0) {
        timeout = setTimeout(() => {
          setTypedNum(fullText.slice(0, typedNum.length - 1));
        }, 180);
      } else {
        // Brief pause when erased before typing repeats
        timeout = setTimeout(() => {
          setIsDeleting(false);
        }, 700);
      }
    }

    return () => clearTimeout(timeout);
  }, [typedNum, isDeleting]);

  return (
    <div className="bg-[#E8F4FB] border border-[#D7E4EE] rounded-2xl p-4 sm:p-6 shadow-2xs">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-2 max-w-3xl">
          <div className="flex items-center gap-3.5">
            {/* Agent 72 AI Bot Image (Enlarged) */}
            <div className="w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 rounded-2xl overflow-hidden border border-[#D7E4EE] bg-white p-2 shadow-xs shrink-0 flex items-center justify-center hover:scale-105 transition-transform duration-300">
              <img
                src={agent72Robot}
                alt="Agent 72 Strategic Decision Advisor"
                className="w-full h-full object-contain"
              />
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-[#163A63] tracking-tight flex items-center">
                  <span>Agent&nbsp;</span>
                  <span className="text-indigo-700 font-mono tracking-wider inline-block">
                    {typedNum}
                    <span className="inline-block animate-cursor-blink text-indigo-500 font-light ml-0.5">
                      |
                    </span>
                  </span>
                </h1>
                <span className="text-[11px] sm:text-xs font-bold text-[#2F6EA6] px-2.5 py-0.5 rounded-full bg-white border border-[#D7E4EE] shadow-2xs">
                  Strategic Planning Agent
                </span>
              </div>
              <div className="text-[11px] sm:text-xs font-bold text-[#2F6EA6] flex items-center gap-1.5 mt-1">
                <span>Evidence</span>
                <ArrowRight className="w-3 h-3 text-[#163A63]" />
                <span>Intelligence</span>
                <ArrowRight className="w-3 h-3 text-[#163A63]" />
                <span>Strategic Action</span>
              </div>
            </div>
          </div>

          <p className="text-xs sm:text-[13px] text-[#19324A] leading-relaxed pt-1">
            Agent 72 converts institutional evidence into strategic intelligence, evaluated options, and measurable planning artifacts for leadership decision support. Final strategic choices, resource allocation, and governance remain with institutional leadership.
          </p>
        </div>

        <div className="hidden md:flex flex-col items-end shrink-0 text-right space-y-1.5 bg-white/70 backdrop-blur-xs p-3 rounded-xl border border-[#D7E4EE]">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#163A63]">
            <ShieldCheck className="w-4 h-4 text-[#16805C]" />
            <span>Deterministic Analysis</span>
          </div>
          <p className="text-[11px] text-[#6B7F91]">
            Evidence-grounded decision support
          </p>
        </div>
      </div>
    </div>
  );
};

