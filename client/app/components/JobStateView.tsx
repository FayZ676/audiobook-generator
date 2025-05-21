import React from "react";

import { AudiobookJob } from "../actions/job";

interface JobStateViewProps {
  jobState: AudiobookJob | null;
}

export default function JobStateView({ jobState }: JobStateViewProps) {
  return <div>{jobState?.script_status || jobState?.narration_status}</div>;
}
