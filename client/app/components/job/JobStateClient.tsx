"use client";

import React from "react";
import { use } from "react";
import { useRouter, useParams } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";
import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";
import type { AudiobookJob } from "@/app/actions/job";
import type { Script } from "@/app/actions/script";
import Tip from "../ui/Tip";
import NarrationProgress from "../narration/NarrationProgress";
import { calculateWordCount } from "@/app/utils/narrationEstimation";

interface JobStateClientProps {
  jobStatePromise: Promise<AudiobookJob | null>;
  scriptPromise: Promise<Script | null> | null;
}

function calculateNarrationWordCount(
  script: Script,
  processingSegmentIds?: string[] | null
): number {
  let toCount;

  if (!processingSegmentIds || processingSegmentIds.length === 0) {
    toCount = script;
  } else {
    const processingSegments = script.segments.filter(
      (seg) => seg.id && processingSegmentIds.includes(seg.id)
    );
    toCount = { ...script, segments: processingSegments };
  }

  return calculateWordCount(toCount);
}

export default function JobStateClient({
  jobStatePromise,
  scriptPromise,
}: JobStateClientProps) {
  const router = useRouter();
  const params = useParams();
  const selectedChapter = params.chapter
    ? decodeURIComponent(params.chapter as string)
    : null;

  const jobState = use(jobStatePromise);
  const script = selectedChapter && scriptPromise ? use(scriptPromise) : null;
  const userChannels = useUserChannels();

  usePusherSubscriptions({
    channels: userChannels
      ? [userChannels.SPEECH_CHANNEL, userChannels.SCRIPT_CHANNEL]
      : null,
    onUpdate: async () => {
      await handleRevalidateTag("job");
      router.refresh();
    },
  });

  return (
    <div>
      {jobState?.script_status && jobState?.script_status === "processing" && (
        <>
          <Tip variant="info">
            Generating script{" "}
            <span className="loading loading-dots loading-xs"></span>
          </Tip>
        </>
      )}
      {jobState?.narration_status &&
        jobState?.narration_status === "processing" && (
          <>
            {script ? (
              <NarrationProgress
                narrationStartedAt={jobState.narration_started_at}
                wordCount={calculateNarrationWordCount(
                  script,
                  jobState?.processing_segment_ids
                )}
              />
            ) : (
              <>
                Generating narration{" "}
                <span className="loading loading-dots loading-xs"></span>
              </>
            )}
          </>
        )}
      {jobState?.script_status && jobState?.script_status === "failed" && (
        <Tip variant="warning">
          Script processing failed. {jobState.message} Try again.
        </Tip>
      )}
      {jobState?.narration_status &&
        jobState?.narration_status === "failed" && (
          <Tip variant="warning">
            Narration processing failed. {jobState.message} Try again.
          </Tip>
        )}
    </div>
  );
}
