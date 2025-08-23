"use client";

import React from "react";
import { use } from "react";
import { useRouter, useParams } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";
import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";

import { getJobState } from "../../actions/job";
import { getScript } from "../../actions/script";
import Tip from "../ui/Tip";
import NarrationProgress from "../narration/NarrationProgress";

export default function JobStateClient() {
  const router = useRouter();
  const params = useParams();
  const selectedChapter = params.chapter
    ? decodeURIComponent(params.chapter as string)
    : null;

  const jobState = use(getJobState());
  const script = selectedChapter ? use(getScript(selectedChapter)) : null;
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
