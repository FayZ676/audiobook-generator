"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";
import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { NARRATION_CHANNEL, SCRIPT_CHANNEL } from "@/app/lib/pusher-channels";

import { AudiobookJob } from "../../actions/job";
import { Script } from "../../actions/script";
import Tip from "../ui/Tip";
import NarrationProgress from "../narration/NarrationProgress";

interface JobStateSectionProps {
  jobStatePromise: Promise<AudiobookJob | null>;
  scriptPromise: Promise<Script | null>;
}

export default function JobStateClient({
  jobStatePromise,
  scriptPromise,
}: JobStateSectionProps) {
  const router = useRouter();
  const jobState = use(jobStatePromise);
  const script = use(scriptPromise);

  usePusherSubscriptions({
    channels: [NARRATION_CHANNEL, SCRIPT_CHANNEL],
    onUpdate: () => {
      handleRevalidateTag("job");
      router.refresh();
    },
  });

  return (
    <div className="flex flex-col gap-2">
      {jobState?.narration_status &&
        jobState?.narration_status === "complete" && (
          <Tip variant="success">Narration generated!</Tip>
        )}
      {jobState?.script_status &&
        jobState?.script_status === "complete" &&
        !jobState?.narration_status && (
          <Tip variant="success">Script generated!</Tip>
        )}
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
                script={script}
                narrationStartedAt={jobState.narration_started_at}
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
