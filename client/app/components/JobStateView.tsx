import React from "react";
import { Suspense } from "react";

import { getJobState } from "../actions/job";
import JobStateClient from "./JobStateClient";

export default function JobStateView() {
  const jobStatePromise = getJobState();
  return (
    <Suspense fallback={<div>Loading job state...</div>}>
      <JobStateClient jobStatePromise={jobStatePromise} />
    </Suspense>
  );
}
