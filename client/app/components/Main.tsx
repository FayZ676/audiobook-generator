"use client";

import React from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Script } from "@/app/actions/script";
import { AudiobookJob } from "@/app/actions/job";
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
  hasNarration: boolean;
  userId: string;
  jobState: AudiobookJob | null;
}

export default function Main({
  createScript,
  createNarration,
  script,
  hasNarration,
  userId,
  jobState,
}: MainProps) {
  const router = useRouter();

  useEffect(() => {
    const channel = pusherClient.subscribe("job-channel");

    channel.bind("job-completed", () => {
      revalidate();
      router.refresh();
    });

    channel.bind("job-status-update", () => {
      revalidate();
      router.refresh();
    });

    return () => {
      channel.unbind("job-completed");
      channel.unbind("job-status-update");
      pusherClient.unsubscribe("job-channel");
    };
  }, [router]);

  return (
    <div className="max-w-md mx-auto">
      {script || jobState?.script_status || jobState?.narration_status ? (
        <div className="flex flex-col gap-4">
          <JobStateView jobState={jobState} />
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
          {hasNarration ? (
            <NarrationView userId={userId} />
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
