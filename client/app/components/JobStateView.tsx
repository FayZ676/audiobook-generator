import React from "react";

interface JobStateViewProps {
  status: string;
}

export default function JobStateView({ status }: JobStateViewProps) {
  return <div>{status}</div>;
}
