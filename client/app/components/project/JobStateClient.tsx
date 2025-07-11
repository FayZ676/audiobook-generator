"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";
import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { NARRATION_CHANNEL, SCRIPT_CHANNEL } from "@/app/lib/pusher-channels";

import { AudiobookJob } from "../../actions/job";
import Tip from "../ui/Tip";
import NarrationProgress from "../narration/NarrationProgress";

interface ScriptInfo {
  filename: string;
  s3_key: string;
}

interface JobStateSectionProps {
  jobStatePromise: Promise<AudiobookJob | null>;
  scriptsPromise: Promise<ScriptInfo[]>;
}

export default function JobStateClient({
  jobStatePromise,
  scriptsPromise,
}: JobStateSectionProps) {
  const router = useRouter();
  const jobState = use(jobStatePromise);
  const scripts = use(scriptsPromise);

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
            <div>
              Generating narration{" "}
              <span className="loading loading-dots loading-xs"></span>
            </div>
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
