"use client";

import React from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Script } from "@/app/actions/script";
import { NarrationUrl } from "../actions/narrate";
import { revalidate } from "@/app/actions/revalidate";

import pusherClient from "@/app/lib/pusher";

import GenerateScriptForm from "@/app/components/GenerateScriptForm";
import ScriptView from "@/app/components/ScriptView";
import NarrationView from "./NarrationView";
import { deleteProject } from "../actions/audiobook";

interface MainProps {
  script: Script | null;
  narrationUrl: NarrationUrl | null;
  createProject: (formData: FormData) => Promise<void>;
}

interface WebhookResponseResultData {
  filename: string;
}

interface WebhookResponseResult {
  event: string;
  job_id: string;
  status: string;
  data: WebhookResponseResultData;
}

export default function Main({
  script,
  narrationUrl,
  createProject,
}: MainProps) {
  const router = useRouter();

  useEffect(() => {
    const channel = pusherClient.subscribe("job-channel");
    channel.bind("job-completed", (data: WebhookResponseResult) => {
      revalidate();
      router.refresh();
    });
    return () => {
      channel.unbind("job-completed");
      pusherClient.unsubscribe("job-channel");
    };
  }, []);

  return (
    <div className="max-w-md mx-auto">
      {script || narrationUrl ? (
        <div className="flex flex-col gap-4">
          <button onClick={deleteProject} className="ml-auto border py-2 px-4">
            Delete Project
          </button>
          {narrationUrl && <NarrationView narrationUrl={narrationUrl} />}
          {script && <ScriptView script={script} />}
        </div>
      ) : (
        <GenerateScriptForm action={createProject} />
      )}
    </div>
  );
}
