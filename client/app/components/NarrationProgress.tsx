"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Script } from "../actions/script";
import { calculateWordCount, estimateNarrationDuration } from "../utils/narrationEstimation";

interface NarrationProgressProps {
  script: Script;
}

export default function NarrationProgress({ script }: NarrationProgressProps) {
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isFinishing, setIsFinishing] = useState(false);

  const wordCount = useMemo(() => calculateWordCount(script), [script]);
  const estimatedDurationSeconds = useMemo(() => estimateNarrationDuration(wordCount), [wordCount]);

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setElapsedTime(elapsed);
      
      const currentProgress = Math.min(100, (elapsed / estimatedDurationSeconds) * 100);
      setProgress(currentProgress);
      
      if (currentProgress >= 100 && !isFinishing) {
        setIsFinishing(true);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [estimatedDurationSeconds, isFinishing]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium">
          {isFinishing ? "Adding finishing touches..." : "Generating narration"}
        </span>
        <span className="text-sm text-gray-500">
          {formatTime(elapsedTime)} / ~{formatTime(estimatedDurationSeconds)}
        </span>
      </div>
      
      <progress 
        className="progress progress-primary w-full" 
        value={progress} 
        max="100"
      >
        {Math.round(progress)}%
      </progress>
      
      <div className="text-xs text-gray-500">
        {wordCount.toLocaleString()} words • Estimated {Math.round(estimatedDurationSeconds / 60)} minutes
      </div>
    </div>
  );
}