"use client";

import React, { use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { SCRIPT_CHANNEL } from "@/app/lib/pusher-channels";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";

import ScriptControls from "./ScriptControls";
import ScriptList from "./ScriptList";

interface ScriptInfo {
  filename: string;
  s3_key: string;
}

interface ScriptManagerClientProps {
  scriptsPromise: Promise<ScriptInfo[]>;
  voicesPromise: Promise<Voice[]>;
  narrationUrlPromise: Promise<string | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function ScriptManagerClient({
  scriptsPromise,
  voicesPromise,
  narrationUrlPromise,
  jobStatePromise,
}: ScriptManagerClientProps) {
  const router = useRouter();

  const scripts = use(scriptsPromise);

  usePusherSubscriptions({
    channels: [SCRIPT_CHANNEL],
    onUpdate: () => {
      handleRevalidateTag("script");
      router.refresh();
    },
  });

  // Get the first script for backward compatibility with existing logic
  const firstScript = scripts.length > 0 ? scripts[0] : null;

  return (
    <div className="flex flex-col gap-4">
      <ScriptList
        scriptsPromise={scriptsPromise}
        voicesPromise={voicesPromise}
        jobStatePromise={jobStatePromise}
      />
      <ScriptControls
        narrationUrlPromise={narrationUrlPromise}
        hasScripts={scripts.length > 0}
        firstScriptFilename={firstScript?.filename}
        jobStatePromise={jobStatePromise}
      />
    </div>
  );
}
