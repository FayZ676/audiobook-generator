import React from "react";

import { revalidate } from "@/app/actions/revalidate";
import { deleteProject } from "@/app/actions/audiobook";

import pusherClient from "@/app/lib/pusher";

import ScriptSection from "@/app/components/ScriptSection";
import NarrationSection from "@/app/components/NarrationSection";
import JobStateView from "./JobStateView";

export default function Main() {
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
    <div className="flex flex-col gap-4">
      <JobStateView />
      <form action={deleteProject}>
        <button className="ml-auto border py-2 px-4">Delete Project</button>
      </form>
      <NarrationSection />
      <ScriptSection />
    </div>
  );
}
