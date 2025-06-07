"use client";

import React from "react";
import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";

import pusherClient from "@/app/lib/pusher";

import { Script } from "../actions/script";

import GenerateScriptForm from "./GenerateScriptForm";
import ScriptText from "./ScriptText";

interface ScriptClientProps {
  scriptPromise: Promise<Script | null>;
}

export default function ScriptClient({ scriptPromise }: ScriptClientProps) {
  const router = useRouter();

  const script = use(scriptPromise);

  useEffect(() => {
    const channel = pusherClient.subscribe("script-channel");
    channel.bind("script-update", () => {
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
      {script ? <ScriptText script={script} /> : <GenerateScriptForm />}
    </div>
  );
}
