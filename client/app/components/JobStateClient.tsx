"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";
import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { NARRATION_CHANNEL, SCRIPT_CHANNEL } from "@/app/lib/pusher-channels";

import { AudiobookJob } from "../actions/job";

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
    <div>
      {jobState?.script_status && `Script: ${jobState.script_status}`}
      {!jobState?.script_status &&
        jobState?.narration_status &&
        `Narration: ${jobState.narration_status}`}
    </div>
  );
}
