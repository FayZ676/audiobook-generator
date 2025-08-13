"use client";

import React, { use } from "react";

import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";
import { Script } from "../../actions/script";
import { AudioSegmentData } from "../../types";

import ChapterControls from "./ChapterControls";
import ScriptEditor from "../script/ScriptEditor";
import NarrationAudio from "../narration/NarrationAudio";

interface ChapterContentProps {
  selectedChapter: string;
  currentScript: Script;
  narrationUrl: string | null;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  voicesPromise: Promise<Voice[]>;
  audioSegmentData: AudioSegmentData;
}

export default function ChapterContent({
  selectedChapter,
  currentScript,
  narrationUrl,
  scriptPromise,
  jobStatePromise,
  voicesPromise,
  audioSegmentData,
}: ChapterContentProps) {
  const jobState = use(jobStatePromise);
  const processingSegmentIds = jobState?.processing_segment_ids || undefined;

  return (
    <>
      {narrationUrl ? (
        <NarrationAudio narrationUrl={narrationUrl} />
      ) : (
        <ChapterControls
          scriptPromise={scriptPromise}
          jobStatePromise={jobStatePromise}
          chapterName={selectedChapter}
        />
      )}

      <ScriptEditor
        script={currentScript}
        voicesPromise={voicesPromise}
        chapterName={selectedChapter}
        processingSegmentIds={processingSegmentIds}
        audioSegmentData={audioSegmentData}
      />
    </>
  );
}
