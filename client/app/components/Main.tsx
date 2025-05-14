"use client";

import React from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Script } from "@/app/actions/script";
import { revalidate } from "@/app/actions/revalidate";

import pusherClient from "@/app/lib/pusher";
import UploadFileForm from "./UploadFileForm";
import CreateScriptForm from "./CreateScriptForm";

interface MainProps {
  script: Script;
  uploadTextFile: (formData: FormData) => Promise<void>;
  createScript: (formData: FormData) => Promise<void>;
  deleteScript: (filename: string) => Promise<void>;
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
  uploadTextFile,
  createScript,
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
      {script ? (
        <div>Script data displayed here.</div>
      ) : (
        <>
          <UploadFileForm action={uploadTextFile} />
          <CreateScriptForm action={createScript} />
        </>
      )}
    </div>
  );
}
