"use client";

import React from "react";
import { use } from "react";

import { AudiobookJob } from "../actions/job";

interface JobStateViewProps {
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function JobStateClient({ jobStatePromise }: JobStateViewProps) {
  const jobState = use(jobStatePromise);
  return <div>{jobState?.script_status || jobState?.narration_status}</div>;
}
