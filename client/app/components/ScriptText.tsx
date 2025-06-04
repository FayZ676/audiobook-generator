import React from "react";

import { Script } from "../actions/script";

interface ScriptTextProps {
  script: Script;
}

export default function ScriptText({ script }: ScriptTextProps) {
  return (
    <div className="bg-gray-50 p-4 rounded">
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
