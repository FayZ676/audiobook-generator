import React, { useState } from "react";

import { Script } from "../actions/script";
import { Voice } from "../actions/voices";
import ScriptEditor from "./ScriptEditor";
import ScriptControls from "./ScriptControls";

interface ScriptTextProps {
  script: Script;
  voices: Voice[];
}

export default function ScriptText({ script, voices }: ScriptTextProps) {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="flex flex-col gap-4">
      <ScriptControls
        isEditing={isEditing}
        onToggleEditing={setIsEditing}
        voices={voices}
      />

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
