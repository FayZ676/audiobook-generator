"use client";

import React from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Script } from "@/app/actions/script";

import pusherClient from "@/app/lib/pusher";

interface MainProps {
  scripts: Script[];
  uploadTextFile: (formData: FormData) => Promise<void>;
  createScript: (formData: FormData) => Promise<void>;
}

export default function Main({
  scripts,
  uploadTextFile,
  createScript,
}: MainProps) {
  const router = useRouter();
  useEffect(() => {
    const channel = pusherClient.subscribe("job-channel");
    channel.bind("job-completed", (data: { message: string }) => {
      router.refresh();
    });
    return () => {
      channel.unbind_all();
      channel.unsubscribe();
      pusherClient.disconnect();
    };
  }, []);

  return (
    <div className="max-w-md mx-auto">
      <form action={uploadTextFile}>
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
        {scripts.map((script) => (
          <div key={script.filename} className="border p-4">
            <p>{script.filename}</p>
          </div>
        ))}
        {scripts.length === 0 && <p>No scripts available.</p>}
      </div>
    </div>
  );
}
