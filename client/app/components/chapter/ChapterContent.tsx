import React from "react";

import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";
import { Script } from "../../actions/script";

import ChapterControls from "./ChapterControls";
import ScriptText from "../script/ScriptText";
import NarrationAudio from "../narration/NarrationAudio";

interface ChapterContentProps {
  selectedChapter: string;
  currentScript: Script;
  narrationUrl: string | null;
  narrationPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  voicesPromise: Promise<Voice[]>;
  voices: Voice[];
  isEditing: boolean;
  setIsEditing: (editing: boolean) => void;
  audioSegmentIds: string[];
}

export default function ChapterContent({
  selectedChapter,
  currentScript,
  narrationUrl,
  narrationPromise,
  scriptPromise,
  jobStatePromise,
  voicesPromise,
  voices,
  isEditing,
  setIsEditing,
  audioSegmentIds,
}: ChapterContentProps) {
  return (
    <>
      {narrationUrl && <NarrationAudio narrationUrl={narrationUrl} />}

      <ChapterControls
        narrationUrlPromise={narrationPromise}
        scriptPromise={scriptPromise}
        jobStatePromise={jobStatePromise}
        voicesPromise={voicesPromise}
        isEditing={isEditing}
        onEditToggle={setIsEditing}
        chapterName={selectedChapter}
      />

      <ScriptText
        script={currentScript}
        voices={voices}
        isEditing={isEditing}
        chapterName={selectedChapter}
        audioSegmentIds={audioSegmentIds}
      />
    </>
  );
}
