import React from "react";

import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";
import { Script } from "../../actions/script";

import ChapterControls from "./ChapterControls";
import ScriptEditor from "../script/ScriptEditor";
import NarrationAudio from "../narration/NarrationAudio";

interface ChapterContentProps {
  selectedChapter: string;
  currentScript: Script;
  narrationUrl: string | null;
  narrationPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  voices: Voice[];
  audioSegmentIds: string[];
}

export default function ChapterContent({
  selectedChapter,
  currentScript,
  narrationUrl,
  narrationPromise,
  scriptPromise,
  jobStatePromise,
  voices,
  audioSegmentIds,
}: ChapterContentProps) {
  return (
    <>
      {narrationUrl && <NarrationAudio narrationUrl={narrationUrl} />}

      <ChapterControls
        narrationUrlPromise={narrationPromise}
        scriptPromise={scriptPromise}
        jobStatePromise={jobStatePromise}
        chapterName={selectedChapter}
      />

      <ScriptEditor
        script={currentScript}
        voices={voices}
        chapterName={selectedChapter}
        audioSegmentIds={audioSegmentIds}
      />
    </>
  );
}
