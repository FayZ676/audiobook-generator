import React from "react";

import { Script } from "../actions/script";

interface ScriptTextProps {
  script: Script;
}

export default function ScriptText({ script }: ScriptTextProps) {
  return (
    <div className="h-[32rem] overflow-y-scroll bg-gray-50 p-4 rounded">
      {script.map((scriptSegment, index) => {
        // TODO: Don't use index as key.
        return (
          <div key={index} className="mb-4">
            <p>
              <span className="font-medium">
                {scriptSegment.speaker.names[0]}
              </span>
              : {scriptSegment.text}
            </p>
          </div>
        );
      })}
    </div>
  );
}
