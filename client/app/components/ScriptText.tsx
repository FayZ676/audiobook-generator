import React, { useState } from "react";

import { Script } from "../actions/script";
import { Voice } from "../actions/voices";
import Tip from "./Tip";
import ScriptEditor from "./ScriptEditor";

interface ScriptTextProps {
  script: Script;
  voices: Voice[];
}

export default function ScriptText({ script, voices }: ScriptTextProps) {
  const [isEditing, setIsEditing] = useState(false);

  const handleSaveComplete = () => {
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <ScriptEditor
        script={script}
        voices={voices}
        onSave={handleSaveComplete}
        onCancel={handleCancelEdit}
      />
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Script</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            className="btn btn-sm btn-primary"
            disabled={voices.length === 0}
          >
            Edit Script
          </button>
        </div>
      </div>

      {voices.length === 0 && (
        <div className="mb-4">
          <Tip variant="info">
            Add voices to enable script editing functionality.
          </Tip>
        </div>
      )}
      
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
    </div>
  );
}
