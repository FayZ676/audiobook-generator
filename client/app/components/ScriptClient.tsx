"use client";

import React from "react";
import { use } from "react";

import { Script } from "../actions/script";
import GenerateScriptForm from "@/app/components/GenerateScriptForm";

interface ScriptClientProps {
  scriptPromise: Promise<Script | null>;
}

export default function ScriptClient({ scriptPromise }: ScriptClientProps) {
  const script = use(scriptPromise);
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
