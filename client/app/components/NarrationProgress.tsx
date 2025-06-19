"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Script } from "../actions/script";
import {
  calculateWordCount,
  estimateNarrationDuration,
} from "../utils/narrationEstimation";

interface NarrationProgressProps {
  script: Script;
  narrationStartedAt?: string | null;
}

export default function NarrationProgress({ script, narrationStartedAt }: NarrationProgressProps) {
  const [progress, setProgress] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [isFinishing, setIsFinishing] = useState(false);

  const wordCount = useMemo(() => calculateWordCount(script), [script]);
  const estimatedDurationSeconds = useMemo(
    () => estimateNarrationDuration(wordCount),
    [wordCount]
  );

  useEffect(() => {
    if (isFinishing) return;

    // Use server-provided start time if available, otherwise fall back to current time
    const startTime = narrationStartedAt ? new Date(narrationStartedAt).getTime() : Date.now();
    
    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setElapsedSeconds(elapsed);

      const currentProgress = Math.min(
        100,
        (elapsed / estimatedDurationSeconds) * 100
      );
      setProgress(currentProgress);

      if (currentProgress >= 100) {
        setIsFinishing(true);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [estimatedDurationSeconds, isFinishing, narrationStartedAt]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const estimatedMins = Math.floor(estimatedDurationSeconds / 60);
  const estimatedSecs = estimatedDurationSeconds % 60;
  const estimatedFormatted = `${estimatedMins}:${estimatedSecs.toString().padStart(2, '0')}`;

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium">
          {isFinishing ? "Adding finishing touches" : "Generating narration"}{" "}
          <span className="text-xs text-gray-500">
            {formatTime(elapsedSeconds)} / ~{estimatedFormatted}
          </span>
        </span>
        <span className="text-xs text-gray-500">
          {Math.round(progress)}%
        </span>
      </div>

      <progress className="progress w-full" value={progress} max="100">
        {Math.round(progress)}%
      </progress>
      
      <div className="text-xs text-gray-500">
        {wordCount.toLocaleString()} words • Estimated {estimatedMins} minute{estimatedMins !== 1 ? 's' : ''}
      </div>
    </div>
  );
}