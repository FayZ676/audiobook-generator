"use client";

import React from "react";
import { use, useEffect } from "react";

import pusherClient from "@/app/lib/pusher";

import { revalidate } from "@/app/actions/revalidate";

import { Script } from "../actions/script";
import GenerateScriptForm from "@/app/components/GenerateScriptForm";

interface ScriptClientProps {
  scriptPromise: Promise<Script | null>;
}

export default function ScriptClient({ scriptPromise }: ScriptClientProps) {
  const script = use(scriptPromise);

  useEffect(() => {
    const channel = pusherClient.subscribe("script-channel");

    channel.bind("script-complete", (data: {}) => {
      revalidate();
    });

    return () => {
      channel.unbind("script-completed");
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
