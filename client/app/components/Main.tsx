"use client";

import React from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Script } from "@/app/actions/script";
import { AudiobookJob } from "@/app/actions/job";
import { NarrationUrl } from "@/app/actions/narrate";
import { revalidate } from "@/app/actions/revalidate";
import { deleteProject } from "@/app/actions/audiobook";

import pusherClient from "@/app/lib/pusher";

import GenerateScriptForm from "@/app/components/GenerateScriptForm";
import ScriptView from "@/app/components/ScriptView";
import NarrationView from "@/app/components/NarrationView";
import JobStateView from "./JobStateView";

interface MainProps {
  createScript: (formData: FormData) => Promise<void>;
  createNarration: () => Promise<void>;
  script: Script | null;
  getNarrationUrl: () => Promise<NarrationUrl | null>;
  jobState: AudiobookJob | null;
}

export default function Main({
  createScript,
  createNarration,
  script,
  getNarrationUrl,
  jobState,
}: MainProps) {
  const router = useRouter();

  useEffect(() => {
    const channel = pusherClient.subscribe("job-channel");

    channel.bind("job-completed", (data: {}) => {
      revalidate();
      router.refresh();
    });

    channel.bind("job-status-update", (data: {}) => {
      revalidate();
      router.refresh();
    });

    return () => {
      channel.unbind("job-completed");
      channel.unbind("job-status-update");
      pusherClient.unsubscribe("job-channel");
    };
  }, []);

  return (
    <div className="max-w-md mx-auto">
      {script || jobState?.script_status || jobState?.narration_status ? (
        <div className="flex flex-col gap-4">
          <JobStateView jobState={jobState} />
          <div className="flex justify-between">
            <button
              onClick={async (e) => {
                e.preventDefault();
                await deleteProject();
                router.refresh();
              }}
              className="border py-2 px-4"
            >
              Delete Project
            </button>
            
            {script && !jobState?.narration_status && (
              <button
                onClick={async (e) => {
                  e.preventDefault();
                  await createNarration();
                  router.refresh();
                }}
                className="border py-2 px-4"
              >
                Narrate
              </button>
            )}
          </div>
          {jobState?.narration_status === "processing" ? (
            <div className="text-center py-2 bg-yellow-100">
              Narration in progress...
            </div>
          ) : (
            script && <NarrationView getNarrationUrl={getNarrationUrl} />
          )}
          {script && <ScriptView script={script} />}
        </div>
      ) : (
        // Disable the form if the script is already generated
        <GenerateScriptForm action={createScript} />
      )}
    </div>
  );
}
