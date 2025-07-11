import React from "react";
import { Suspense } from "react";

import { AudiobookJob } from "../../actions/job";

import JobStateClient from "./JobStateClient";

interface ScriptInfo {
  filename: string;
  s3_key: string;
}

interface JobStateSectionProps {
  jobStatePromise: Promise<AudiobookJob | null>;
  scriptsPromise: Promise<ScriptInfo[]>;
}

export default function JobStateSection({
  jobStatePromise,
  scriptsPromise,
}: JobStateSectionProps) {
  return (
    <Suspense fallback={<div>Loading job state ...</div>}>
      <JobStateClient 
        jobStatePromise={jobStatePromise} 
        scriptsPromise={scriptsPromise}
      />
    </Suspense>
  );
}
