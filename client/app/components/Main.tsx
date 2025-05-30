import React from "react";

import { AudiobookJob } from "@/app/actions/job";
import { revalidate } from "@/app/actions/revalidate";
import { deleteProject } from "@/app/actions/audiobook";

import pusherClient from "@/app/lib/pusher";

import ScriptView from "@/app/components/ScriptView";
import NarrationView from "@/app/components/NarrationView";
import JobStateView from "./JobStateView";

interface MainProps {
  jobState: AudiobookJob | null;
}

export default function Main({ jobState }: MainProps) {
  useEffect(() => {
    const channel = pusherClient.subscribe("job-channel");

    channel.bind("job-completed", (data: {}) => {
      revalidate();
    });

    channel.bind("job-status-update", (data: {}) => {
      revalidate();
    });

    return () => {
      channel.unbind("job-completed");
      channel.unbind("job-status-update");
      pusherClient.unsubscribe("job-channel");
    };
  }, []);

  return (
    <div className="max-w-md mx-auto">
      {(jobState?.script_status || jobState?.narration_status) && (
        <div className="flex flex-col gap-4">
          <JobStateView jobState={jobState} />
          <form action={deleteProject}>
            <button className="ml-auto border py-2 px-4">Delete Project</button>
          </form>
          <NarrationView />
          <ScriptView />
        </div>
      )}
    </div>
  );
}
