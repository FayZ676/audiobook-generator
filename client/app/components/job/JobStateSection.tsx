import React from "react";

import { AudiobookJob } from "../../actions/job";
import { Script } from "../../actions/script";

import JobStateClient from "./JobStateClient";

interface JobStateSectionProps {
  jobStatePromise: Promise<AudiobookJob | null>;
  scriptPromise: Promise<Script | null>;
}

export default function JobStateSection({
  jobStatePromise,
  scriptPromise,
}: JobStateSectionProps) {
  return (
    <JobStateClient
      jobStatePromise={jobStatePromise}
      scriptPromise={scriptPromise}
    />
  );
}
