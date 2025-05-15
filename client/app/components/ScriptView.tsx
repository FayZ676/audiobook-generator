import React from "react";

import { Script } from "@/app/actions/script";

interface ScriptViewProps {
  script: Script;
}

export default function ScriptView({ script }: ScriptViewProps) {
  return (
    <div>
      {script.map((scriptSegment, index) => {
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
