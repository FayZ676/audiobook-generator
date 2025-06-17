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
        <ul className="menu menu-horizontal bg-base-200 rounded-box">
          <li>
            <a 
              className={!isEditing ? "active" : ""}
              onClick={() => setIsEditing(false)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </a>
          </li>
          <li>
            <a 
              className={isEditing ? "active" : ""}
              onClick={() => setIsEditing(true)}
              title={voices.length === 0 ? "Add voices to enable editing" : "Edit script"}
              style={voices.length === 0 ? { pointerEvents: 'none', opacity: 0.5 } : {}}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </a>
          </li>
        </ul>
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
