"use client";

import React from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Script } from "@/app/actions/script";
import { revalidate } from "@/app/actions/revalidate";

import pusherClient from "@/app/lib/pusher";

interface MainProps {
  scripts: Script[];
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
  scripts,
  uploadTextFile,
  createScript,
  deleteScript,
}: MainProps) {
  const router = useRouter();
  useEffect(() => {
    const channel = pusherClient.subscribe("job-channel");
    channel.bind(
      "job-completed",
      (data: { payload: WebhookResponseResult }) => {
        revalidate();
        router.refresh();
      }
    );
    return () => {
      channel.unbind_all();
      channel.unsubscribe();
      pusherClient.disconnect();
    };
  }, []);

  return (
    <div className="max-w-md mx-auto">
      <form action={uploadTextFile} className="flex flex-col gap-4 max-w-sm">
        <label htmlFor="file-input">Upload Text File</label>
        <input
          id="file-input"
          name="file"
          type="file"
          accept=".txt"
          className="border"
        />
        <button type="submit">Upload</button>
      </form>

      <form action={createScript} className="flex flex-col gap-4 max-w-sm">
        <h2>Generate Script</h2>
        <label htmlFor="filename-input">File Name</label>
        <input
          id="filename-input"
          name="filename"
          type="text"
          className="border"
        />
        <label htmlFor="narrator-input">Narrator Voice Name</label>
        <input
          id="narrator-input"
          name="narrator"
          type="text"
          className="border"
        />
        <button type="submit">Submit</button>
      </form>

      <div className="flex flex-col gap-4">
        <h2>Scripts</h2>
        {scripts.map((script) => (
          <div
            key={script.filename}
            className="flex justify-between border p-4"
          >
            <p>{script.filename}</p>
            <button
              onClick={async () => {
                await deleteScript(script.filename);
              }}
            >
              Delete
            </button>
          </div>
        ))}
        {scripts.length === 0 && <p>No scripts available.</p>}
      </div>
    </div>
  );
}
