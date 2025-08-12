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
}

export default async function ChapterContent({
  selectedChapter,
  currentScript,
  narrationUrl,
  narrationPromise,
  scriptPromise,
  jobStatePromise,
  voices,
}: ChapterContentProps) {
  const jobState = await jobStatePromise;
  const processingSegmentIds = jobState?.processing_segment_ids || undefined;

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
        processingSegmentIds={processingSegmentIds}
      />
    </>
  );
}
