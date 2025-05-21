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
  narrationUrl: NarrationUrl | null;
  jobState: AudiobookJob | null;
}

interface WebhookResponseResultData {
  filename: string;
}

export default function Main({
  createScript,
  createNarration,
  script,
  narrationUrl,
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
      {jobState && <JobStateView status={jobState.status} />}
      {script ? (
        <div className="flex flex-col gap-4">
          <button
            onClick={async (e) => {
              e.preventDefault();
              await deleteProject();
              router.refresh();
            }}
            className="ml-auto border py-2 px-4"
          >
            Delete Project
          </button>
          {narrationUrl ? (
            <NarrationView narrationUrl={narrationUrl} />
          ) : (
            <button
              onClick={async (e) => {
                e.preventDefault();
                await createNarration();
                router.refresh();
              }}
              className="ml-auto border py-2 px-4"
            >
              Narrate
            </button>
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
