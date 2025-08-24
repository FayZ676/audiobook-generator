"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";
import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";
import type { AudiobookJob } from "@/app/actions/job";
import type { Script } from "@/app/actions/script";
import Tip from "../ui/Tip";

interface JobStateClientProps {
  jobStatePromise: Promise<AudiobookJob | null>;
  scriptPromise: Promise<Script | null> | null;
}

export default function JobStateClient({
  jobStatePromise,
}: JobStateClientProps) {
  const router = useRouter();
  const jobState = use(jobStatePromise);
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
            <Tip variant="info">
              Generating Narration{" "}
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
