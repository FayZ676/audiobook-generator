"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";
import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { getUserSpecificChannels } from "@/app/lib/pusher-channels";
import type { AudiobookJob } from "@/app/actions/job";
import Tip from "../ui/Tip";

interface JobStateClientProps {
  userId: string;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function JobStateClient({
  userId,
  jobStatePromise,
}: JobStateClientProps) {
  const router = useRouter();
  const jobState = use(jobStatePromise);
  const userChannels = getUserSpecificChannels(userId);

  usePusherSubscriptions({
    channels: [userChannels.SPEECH_CHANNEL, userChannels.SCRIPT_CHANNEL],
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
