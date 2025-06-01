"use client";

import React from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import pusherClient from "@/app/lib/pusher";

import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Script } from "../actions/script";

interface ScriptTextClientProps {
  script: Script | null;
}

export default function ScriptTextClient({ script }: ScriptTextClientProps) {
  const router = useRouter();

  useEffect(() => {
    const channel = pusherClient.subscribe("script-channel");

    channel.bind("script-update", (data: {}) => {
      console.log("Script updated");
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
      {script &&
        script.map((scriptSegment, index) => {
          // TODO: Don't use index as key.
          return (
            <div key={index} className="mb-4">
              <p>
                {scriptSegment.speaker.names[0]}: {scriptSegment.text}
              </p>
            </div>
          );
        })}
    </div>
  );
}
