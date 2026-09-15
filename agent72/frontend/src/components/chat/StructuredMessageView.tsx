import React from 'react';

interface StructuredMessageViewProps {
  content: string;
}

export const StructuredMessageView: React.FC<StructuredMessageViewProps> = ({ content }) => {
  // Split lines
  const lines = content.split('\n');

  const elements: React.ReactNode[] = [];
  let currentTableLines: string[] = [];
  let inTable = false;

  const flushTable = (key: string) => {
    if (currentTableLines.length < 2) {
      // Not a valid table, render as plain lines
      currentTableLines.forEach((tl, idx) => {
        elements.push(
          <div key={`${key}-fallback-${idx}`} className="py-0.5">
            {renderInlineMarkdown(tl)}
          </div>
        );
      });
      currentTableLines = [];
      inTable = false;
      return;
    }

    // Parse table
    const headerLine = currentTableLines[0];
    const dataLines = currentTableLines.slice(1).filter((l) => !l.includes('---'));

    const headers = headerLine
      .split('|')
      .map((c) => c.trim())
      .filter((c, idx, arr) => idx !== 0 && idx !== arr.length - 1 || c.length > 0);

    const rows = dataLines.map((line) =>
      line
        .split('|')
        .map((c) => c.trim())
        .filter((c, idx, arr) => idx !== 0 && idx !== arr.length - 1 || c.length > 0)
    );

    elements.push(
      <div
        key={key}
        className="my-2.5 sm:my-3 overflow-x-auto rounded-lg sm:rounded-xl border border-slate-200 shadow-2xs bg-white max-w-full touch-pan-x -mx-1 sm:mx-0"
        style={{ WebkitOverflowScrolling: 'touch' }}
      >
        {headers.length > 3 && (
          <div className="sm:hidden text-[9.5px] text-slate-400 px-2.5 pt-1.5 font-medium flex items-center justify-between select-none">
            <span>Table data</span>
            <span className="text-inst-blue font-semibold">Swipe horizontally &rarr;</span>
          </div>
        )}
        <table className="min-w-full text-left text-[11px] sm:text-xs border-collapse">
          <thead className="bg-slate-100/90 text-slate-700 font-semibold border-b border-slate-200">
            <tr>
              {headers.map((h, hIdx) => (
                <th key={hIdx} className="px-2.5 py-1.5 sm:px-3 sm:py-2 whitespace-nowrap">
                  {renderInlineMarkdown(h)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {rows.map((row, rIdx) => (
              <tr key={rIdx} className={rIdx % 2 === 1 ? 'bg-slate-50/50' : 'bg-white'}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-2.5 py-1.5 sm:px-3 sm:py-2 leading-snug whitespace-normal break-words">
                    {renderInlineMarkdown(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );

    currentTableLines = [];
    inTable = false;
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    // Check if table row
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      inTable = true;
      currentTableLines.push(trimmed);
      return;
    }

    if (inTable) {
      flushTable(`tbl-${index}`);
    }

    if (!trimmed) {
      elements.push(<div key={`spacer-${index}`} className="h-1 sm:h-1.5" />);
      return;
    }

    // Section headers
    if (trimmed.startsWith('## ')) {
      elements.push(
        <h3
          key={`h2-${index}`}
          className="text-xs sm:text-base font-bold text-slate-800 pt-2 pb-1 border-b border-slate-200 flex items-center gap-1.5 break-words"
        >
          {renderInlineMarkdown(trimmed.replace('## ', ''))}
        </h3>
      );
      return;
    }

    if (trimmed.startsWith('### ')) {
      elements.push(
        <h4
          key={`h3-${index}`}
          className="text-[11.5px] sm:text-sm font-bold text-blue-900 pt-2 pb-0.5 break-words"
        >
          {renderInlineMarkdown(trimmed.replace('### ', ''))}
        </h4>
      );
      return;
    }

    // Bullets
    if (trimmed.startsWith('• ') || trimmed.startsWith('- ')) {
      elements.push(
        <div key={`bullet-${index}`} className="flex items-start gap-1.5 pl-0.5 sm:pl-1 py-0.5 text-xs text-slate-700 break-words">
          <span className="text-blue-500 font-bold shrink-0 mt-0.5">•</span>
          <div className="flex-1 leading-relaxed break-words min-w-0">
            {renderInlineMarkdown(trimmed.slice(2))}
          </div>
        </div>
      );
      return;
    }

    // Regular line
    elements.push(
      <div key={`p-${index}`} className="py-0.5 leading-relaxed break-words">
        {renderInlineMarkdown(line)}
      </div>
    );
  });

  if (inTable) {
    flushTable(`tbl-final`);
  }

  return <div className="space-y-1 overflow-hidden">{elements}</div>;
};

// Inline markdown formatting (bold, code, italics)
function renderInlineMarkdown(text: string): React.ReactNode {
  if (!text) return null;

  // Split by code blocks first
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g);

  return parts.map((part, i) => {
    if (part.startsWith('`') && part.endsWith('`')) {
      const code = part.slice(1, -1);
      const isRed = code.includes('CRITICAL') || code.includes('AT_RISK') || code.includes('DECLIN');
      const isGreen = code.includes('IMPROV') || code.includes('HIGH');
      return (
        <span
          key={i}
          className={`font-mono text-[11px] px-1 py-0.2 rounded font-semibold ${
            isRed
              ? 'bg-rose-50 text-rose-700 border border-rose-200'
              : isGreen
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              : 'bg-slate-100 text-slate-800 border border-slate-200'
          }`}
        >
          {code}
        </span>
      );
    }

    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-slate-900">
          {part.slice(2, -2)}
        </strong>
      );
    }

    if (part.startsWith('*') && part.endsWith('*')) {
      return (
        <em key={i} className="text-slate-500 italic">
          {part.slice(1, -1)}
        </em>
      );
    }

    return part;
  });
}
