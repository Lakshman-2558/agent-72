import React, { useState } from 'react';
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize2,
  MoreVertical,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

interface EventCompetition {
  id: string;
  title: string;
  category: string;
  duration: string;
  gradient: string;
  accent: string;
  tag: string;
}

export const EventHighlightsPanel: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [activeSlide, setActiveSlide] = useState(0);

  const competitions: EventCompetition[] = [
    {
      id: 'music',
      title: 'AI MUSICAL COMPETITION',
      category: 'Audio & Generative Music',
      duration: '0:45',
      gradient: 'from-[#1e1b4b] via-[#312e81] to-[#4c1d95]',
      accent: '#c084fc',
      tag: 'AGENTIC AI DAY 2026',
    },
    {
      id: 'reels',
      title: 'AI REELS COMPETITION',
      category: 'Visual Synthesis & Video',
      duration: '0:40',
      gradient: 'from-[#0f172a] via-[#1e1b4b] to-[#701a75]',
      accent: '#f472b6',
      tag: 'CREATIVE TRACK',
    },
    {
      id: 'quiz',
      title: 'AI QUIZ COMPETITION',
      category: 'LLM & Technical Hackathon',
      duration: '0:35',
      gradient: 'from-[#082f49] via-[#0c4a6e] to-[#1e3a8a]',
      accent: '#38bdf8',
      tag: 'BRAIN CHALLENGE',
    },
    {
      id: 'code',
      title: 'AI HACKATHON & CODING',
      category: 'Agentic Workflow Systems',
      duration: '0:50',
      gradient: 'from-[#064e3b] via-[#065f46] to-[#047857]',
      accent: '#34d399',
      tag: 'GRAND FINALE',
    },
  ];

  const handlePrev = () => {
    setActiveSlide((prev) => (prev === 0 ? competitions.length - 3 : prev - 1));
  };

  const handleNext = () => {
    setActiveSlide((prev) => (prev >= competitions.length - 3 ? 0 : prev + 1));
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs p-4 sm:p-5 flex flex-col h-full space-y-4">
      {/* Title */}
      <h2 className="text-center text-base sm:text-lg font-bold text-slate-800 tracking-tight">
        Highlights
      </h2>

      {/* Featured Video Player */}
      <div className="relative w-full aspect-video rounded-xl overflow-hidden bg-slate-900 border border-slate-200 shadow-xs group">
        {/* Poster / Video Display */}
        <div className="absolute inset-0 bg-gradient-to-r from-amber-950/80 via-slate-900/90 to-amber-950/80 flex items-center justify-center">
          {/* Decorative Hall Entrance Mockup matching screenshot */}
          <div className="w-full h-full relative overflow-hidden flex items-center justify-center">
            {/* Wooden doors architectural design */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-amber-900/50 via-stone-900 to-black opacity-90" />
            <div className="absolute inset-y-0 left-0 w-1/3 bg-amber-950/60 border-r border-amber-800/40 flex items-center justify-end pr-2">
              <div className="w-1.5 h-20 bg-amber-200/60 rounded-full" />
            </div>
            <div className="absolute inset-y-0 right-0 w-1/3 bg-amber-950/60 border-l border-amber-800/40 flex items-center justify-start pl-2">
              <div className="w-1.5 h-20 bg-amber-200/60 rounded-full" />
            </div>

            {/* Center Stage Presentation Character / Faculty */}
            <div className="relative z-10 flex flex-col items-center justify-center text-center space-y-1">
              <div className="w-12 h-12 rounded-full bg-blue-600/90 text-white flex items-center justify-center shadow-lg border border-white/20">
                <Sparkles className="w-6 h-6 text-cyan-300" />
              </div>
              <span className="text-xs font-bold text-white tracking-wide">
                Agentic AI Day 2026 • Live Showcase
              </span>
              <span className="text-[10px] text-slate-300">
                Department of Computer Science & Engineering
              </span>
            </div>
          </div>
        </div>

        {/* Video Control Bar Overlay */}
        <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-2.5 flex flex-col gap-1 z-20">
          {/* Progress Timeline Scrubber */}
          <div className="w-full h-1 bg-white/30 rounded-full overflow-hidden cursor-pointer">
            <div className="h-full bg-blue-500 w-[18%]" />
          </div>

          <div className="flex items-center justify-between text-white text-xs pt-1">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="hover:text-blue-400 transition"
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
              </button>
              <span className="text-[11px] font-mono text-slate-200">0:05 / 0:36</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsMuted(!isMuted)}
                className="hover:text-blue-400 transition"
              >
                {isMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
              </button>
              <Maximize2 className="w-3.5 h-3.5 hover:text-blue-400 transition cursor-pointer" />
              <MoreVertical className="w-3.5 h-3.5 hover:text-blue-400 transition cursor-pointer" />
            </div>
          </div>
        </div>
      </div>

      {/* Competitions Carousel */}
      <div className="relative pt-1">
        <div className="grid grid-cols-3 gap-2.5">
          {competitions.slice(activeSlide, activeSlide + 3).map((item) => (
            <div
              key={item.id}
              className={`relative rounded-xl overflow-hidden aspect-[3/4] bg-gradient-to-b ${item.gradient} p-2.5 flex flex-col justify-between border border-slate-700/50 shadow-xs hover:border-blue-400 transition-all duration-200 cursor-pointer group`}
            >
              {/* Top Mini Badge */}
              <div className="flex items-center justify-between">
                <span className="text-[7.5px] font-extrabold uppercase tracking-wider text-slate-300 bg-black/40 px-1 py-0.5 rounded">
                  {item.tag}
                </span>
              </div>

              {/* Center Graphics / Glow */}
              <div className="flex flex-col items-center justify-center my-auto text-center py-2">
                <div
                  className="text-[10px] sm:text-[11px] font-black tracking-tight leading-tight uppercase"
                  style={{ color: item.accent }}
                >
                  {item.title}
                </div>
                <div className="text-[7.5px] text-slate-300 pt-1 leading-tight line-clamp-2">
                  {item.category}
                </div>
              </div>

              {/* Bottom Duration Badge */}
              <div className="flex items-center justify-end">
                <span className="text-[8.5px] font-mono bg-black/60 text-white px-1.5 py-0.5 rounded font-semibold border border-white/10">
                  {item.duration}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Carousel Prev Button */}
        <button
          onClick={handlePrev}
          className="absolute -left-2.5 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 flex items-center justify-center shadow-md transition z-10"
          title="Previous highlights"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
        </button>

        {/* Carousel Next Button */}
        <button
          onClick={handleNext}
          className="absolute -right-2.5 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 flex items-center justify-center shadow-md transition z-10"
          title="Next highlights"
        >
          <ChevronRight className="w-3.5 h-3.5" />
        </button>

        {/* Pagination Dots */}
        <div className="flex items-center justify-center gap-1.5 pt-3">
          <span className={`w-1.5 h-1.5 rounded-full ${activeSlide === 0 ? 'bg-blue-600' : 'bg-slate-300'}`} />
          <span className={`w-1.5 h-1.5 rounded-full ${activeSlide > 0 ? 'bg-blue-600' : 'bg-slate-300'}`} />
          <span className="w-1.5 h-1.5 rounded-full bg-slate-300" />
        </div>
      </div>
    </div>
  );
};
