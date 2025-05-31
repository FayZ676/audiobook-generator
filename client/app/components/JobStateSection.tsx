import React from "react";
import { Suspense } from "react";

import { AudiobookJob } from "../actions/job";

import JobStateClient from "./JobStateClient";

interface JobStateSectionProps {
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function JobStateSection({
  jobStatePromise,
}: JobStateSectionProps) {
  return (
    <Suspense fallback={<div>Loading job state ...</div>}>
      <JobStateClient jobStatePromise={jobStatePromise} />
    </Suspense>
  );
}
