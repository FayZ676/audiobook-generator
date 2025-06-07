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
    channel.bind("job-update", () => {
      handleRevalidateTag("job");
      router.refresh();
    });

    return () => {
      channel.unbind("job-update");
      pusherClient.unsubscribe("job-channel");
    };
  }, []);

  return <div>{jobState?.script_status || jobState?.narration_status}</div>;
}
