import React, { useMemo } from "react";
import { Script } from "../../actions/script";
import { Voice } from "../../actions/voices";

interface CharacterVoiceMappingProps {
  script: Script;
  voices: Voice[];
  onCharacterVoiceChange: (characterName: string, voiceName: string) => void;
}

interface CharacterMapping {
  characterName: string;
  currentVoice: string;
}

function extractCharacterMappings(script: Script): CharacterMapping[] {
  const characterMap = new Map<string, string>();

  // Use speakers array and voices mapping from Script structure
  script.speakers.forEach((speaker) => {
    const characterName = speaker.names[0];
    if (characterName && characterName.trim()) {
      const voiceName = script.voices[characterName] || '';
      characterMap.set(characterName, voiceName);
    }
  });

  return Array.from(characterMap.entries()).map(
    ([characterName, currentVoice]) => ({
      characterName,
      currentVoice,
    })
  );
}

export default function CharacterVoiceMapping({
  script,
  voices,
  onCharacterVoiceChange,
}: CharacterVoiceMappingProps) {
  const characterMappings = useMemo(
    () => extractCharacterMappings(script),
    [script]
  );

  return (
    <div className="max-h-[14rem] overflow-y-scroll bg-base-200 p-4 rounded">
      <div className="flex flex-col gap-4">
        {characterMappings.map((mapping) => (
          <div key={mapping.characterName} className="grid grid-cols-2">
            <span className="font-medium min-w-[100px] text-sm">
              {mapping.characterName}:
            </span>
            <select
              value={mapping.currentVoice}
              onChange={(e) =>
                onCharacterVoiceChange(mapping.characterName, e.target.value)
              }
              className="select select-sm select-bordered flex-1"
            >
              {voices.map((voice) => (
                <option key={voice.name} value={voice.name}>
                  {voice.name}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}
