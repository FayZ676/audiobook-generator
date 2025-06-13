"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";
import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { NARRATION_CHANNEL, SCRIPT_CHANNEL } from "@/app/lib/pusher-channels";

import { AudiobookJob } from "../actions/job";
import Tip from "./Tip";

interface JobStateSectionProps {
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function JobStateClient({
  jobStatePromise,
}: JobStateSectionProps) {
  const router = useRouter();
  const jobState = use(jobStatePromise);

  usePusherSubscriptions({
    channels: [NARRATION_CHANNEL, SCRIPT_CHANNEL],
    onUpdate: (channel, event, data) => {
      handleRevalidateTag("job");
      router.refresh();
    },
    dependencies: [router],
  });

  return (
    <div className="flex flex-col gap-2">
      {jobState?.script_status && jobState?.script_status === "complete" && (
        <Tip variant="success">Script processing complete!</Tip>
      )}
      {jobState?.narration_status &&
        jobState?.narration_status === "complete" && (
          <Tip variant="success">Narration processing complete!</Tip>
        )}
      {jobState?.script_status && jobState?.script_status === "processing" && (
        <>
          <Tip variant="info">
            Script is being processed{" "}
            <span className="loading loading-dots loading-xs"></span>
          </Tip>
        </>
      )}
      {jobState?.narration_status &&
        jobState?.narration_status === "processing" && (
          <>
            <Tip variant="info">
              Narration is being processed{" "}
              <span className="loading loading-dots loading-xs"></span>
            </Tip>
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
