import React from "react";

import { Script } from "../../actions/script";
import { Voice } from "../../actions/voices";
import ScriptEditor from "./ScriptEditor";

interface ScriptTextProps {
  script: Script;
  voices: Voice[];
  isEditing: boolean;
}

export default function ScriptText({
  script,
  voices,
  isEditing,
}: ScriptTextProps) {
  return (
    <div className="flex flex-col gap-4">
      {isEditing ? (
        <ScriptEditor script={script} voices={voices} />
      ) : (
        <div className="h-[32rem] overflow-y-scroll bg-base-200 p-4 rounded">
          {script.map((scriptSegment, index) => {
            return (
              <div key={index} className="mb-4">
                <p>
                  <span
                    className="font-medium tooltip tooltip-right"
                    data-tip={scriptSegment.voice_name}
                  >
                    {scriptSegment.speaker.names[0]}
                  </span>
                  : {scriptSegment.text}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
