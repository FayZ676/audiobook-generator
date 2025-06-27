import React from "react";

interface DemoAudioProps {
  speaker: string;
  voiceType: string;
  text: string;
  colorClass: string;
}

export default function DemoAudio({ speaker, voiceType, text, colorClass }: DemoAudioProps) {
  return (
    <div className={`flex items-center gap-3 p-3 bg-base-100 rounded border-l-4 ${colorClass}`}>
      <div className="flex-1">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium">{speaker}</span>
          <span className="text-xs text-gray-500">{voiceType}</span>
        </div>
        <div className="text-sm text-gray-700 italic">
          &ldquo;{text}&rdquo;
        </div>
      </div>
      <button className="btn btn-sm btn-ghost" title={`Play ${speaker}'s voice sample`}>
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
        </svg>
      </button>
    </div>
  );
}