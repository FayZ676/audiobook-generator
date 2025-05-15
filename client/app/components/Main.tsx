"use client";

import React from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Script } from "@/app/actions/script";
import { revalidate } from "@/app/actions/revalidate";

import pusherClient from "@/app/lib/pusher";

import GenerateScriptForm from "@/app/components/GenerateScriptForm";
import ScriptView from "@/app/components/ScriptView";

interface MainProps {
  script: Script;
  createScript: (formData: FormData) => Promise<void>;
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

export default function Main({ script, createScript }: MainProps) {
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
      {script ? (
        <ScriptView script={script} />
      ) : (
        <GenerateScriptForm action={createScript} />
      )}
    </div>
  );
}
