import React, { useState } from "react";
import { FileText, Edit3 } from "lucide-react";

import { Script } from "../actions/script";
import { Voice } from "../actions/voices";
import ScriptEditor from "./ScriptEditor";

interface ScriptTextProps {
  script: Script;
  voices: Voice[];
}

export default function ScriptText({ script, voices }: ScriptTextProps) {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-between items-center">
        <h3 className="font-bold">Script controls</h3>
        <ul className="menu menu-horizontal bg-base-200 rounded-box">
          <li>
            <a
              className={!isEditing ? "active" : ""}
              onClick={() => setIsEditing(false)}
            >
              <FileText className="h-5 w-5" />
            </a>
          </li>
          <li>
            <a
              className={isEditing ? "active" : ""}
              onClick={() => setIsEditing(true)}
              title={
                voices.length === 0
                  ? "Add voices to enable editing"
                  : "Edit script"
              }
              style={
                voices.length === 0
                  ? { pointerEvents: "none", opacity: 0.5 }
                  : {}
              }
            >
              <Edit3 className="h-5 w-5" />
            </a>
          </li>
        </ul>
      </div>

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
