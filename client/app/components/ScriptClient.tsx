"use client";

import React from "react";
import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";

import pusherClient from "@/app/lib/pusher";

import { Script } from "../actions/script";

import GenerateScriptForm from "./GenerateScriptForm";

interface ScriptClientProps {
  scriptPromise: Promise<Script | null>;
}

export default function ScriptClient({ scriptPromise }: ScriptClientProps) {
  const router = useRouter();

  const script = use(scriptPromise);

  useEffect(() => {
    const channel = pusherClient.subscribe("script-channel");
    channel.bind("script-update", (data: {}) => {
      handleRevalidateTag("script");
      router.refresh();
    });

    return () => {
      channel.unbind("script-update");
      pusherClient.unsubscribe("script-channel");
    };
  }, []);

  return (
    <div>
      {script ? (
        script.map((scriptSegment, index) => {
          // TODO: Don't use index as key.
          return (
            <div key={index} className="mb-4">
              <p>
                {scriptSegment.speaker.names[0]}: {scriptSegment.text}
              </p>
            </div>
          );
        })
      ) : (
        <GenerateScriptForm />
      )}
    </div>
  );
}
