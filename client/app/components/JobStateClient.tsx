"use client";

import React from "react";
import { use } from "react";

import { AudiobookJob } from "../actions/job";

interface JobStateSectionProps {
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function JobStateClient({
  jobStatePromise,
}: JobStateSectionProps) {
  const jobState = use(jobStatePromise);
  return <div>{jobState?.script_status || jobState?.narration_status}</div>;
}
