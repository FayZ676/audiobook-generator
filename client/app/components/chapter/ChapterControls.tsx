"use client";

import React, { useState } from "react";
import { use } from "react";
import { MicVocal } from "lucide-react";

import { createNarration } from "../../actions/narrate";
import { Script } from "../../actions/script";
import { AudiobookJob } from "../../actions/job";
import Tip from "../ui/Tip";

interface ChapterControlsProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  chapterName: string;
}

export default function ChapterControls({
  narrationUrlPromise,
  scriptPromise,
  jobStatePromise,
  chapterName,
}: ChapterControlsProps) {
  const [isCreatingNarration, setIsCreatingNarration] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const narrationUrl = use(narrationUrlPromise);
  const script = use(scriptPromise);
  const jobState = use(jobStatePromise);

  const handleCreateNarration = async (e: React.MouseEvent) => {
    e.preventDefault();
    setIsCreatingNarration(true);
    setError(null);
    try {
      await createNarration(chapterName);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      setError(errorMessage ? errorMessage : "Something went wrong.");
    } finally {
      setIsCreatingNarration(false);
    }
  };

  const isProcessing =
    jobState?.script_status === "processing" ||
    jobState?.narration_status === "processing";

  return (
    <div className="flex items-center justify-between gap-4">
      {error && <Tip variant="warning">{error}</Tip>}

      <div className="flex gap-2 ml-auto">
        {script && (
          <button
            className="btn btn-info btn-outline"
            onClick={(e) => {
              setError(null);
              handleCreateNarration(e);
            }}
            disabled={isCreatingNarration || isProcessing}
          >
            <MicVocal size={16} className="md:hidden" />
            <span className="hidden md:inline">
              {isCreatingNarration ||
              jobState?.narration_status === "processing"
                ? "Creating..."
                : narrationUrl
                ? "Regenerate"
                : "Narrate"}
            </span>
          </button>
        )}
      </div>
    </div>
  );
}
