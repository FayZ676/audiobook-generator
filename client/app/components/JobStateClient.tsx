"use client";

import React from "react";
import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

import pusherClient from "@/app/lib/pusher";

import { handleRevalidateTag } from "@/app/actions/revalidate";

import { AudiobookJob } from "../actions/job";

interface JobStateSectionProps {
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function JobStateClient({
  jobStatePromise,
}: JobStateSectionProps) {
  const router = useRouter();

  const jobState = use(jobStatePromise);

  useEffect(() => {
    const channel = pusherClient.subscribe("job-channel");
    channel.bind("job-update", (data: {}) => {
      handleRevalidateTag("job");
      router.refresh();
    });

    return () => {
      channel.unbind("job-update");
      pusherClient.unsubscribe("job-channel");
    };
  }, []);

  const getJobStatusMessage = () => {
    if (jobState?.script_status) {
      return `Script ${jobState.script_status}`;
    }
    if (jobState?.narration_status) {
      return `Narration ${jobState.narration_status}`;
    }
    return null;
  };

  return <div>{getJobStatusMessage()}</div>;
}
