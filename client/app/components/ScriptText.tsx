import React from "react";

import { Script } from "../actions/script";
import { Voice } from "../actions/voices";

interface ScriptTextProps {
  script: Script;
  voices: Voice[];
}

export default function ScriptText({ script, voices }: ScriptTextProps) {
  const getVoiceDetails = (voiceName: string): Voice | null => {
    return voices.find(voice => voice.name === voiceName) || null;
  };

  return (
    <div className="h-[32rem] overflow-y-scroll bg-base-200 p-4 rounded">
      {script.map((scriptSegment, index) => {
        // TODO: Don't use index as key.
        const voiceDetails = getVoiceDetails(scriptSegment.voice_name);
        const tooltipContent = voiceDetails 
          ? `${voiceDetails.name} • ${voiceDetails.gender} • ${voiceDetails.age}`
          : scriptSegment.voice_name;

        return (
          <div key={index} className="mb-4">
            <p>
              <span 
                className="font-medium tooltip" 
                data-tip={tooltipContent}
              >
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
