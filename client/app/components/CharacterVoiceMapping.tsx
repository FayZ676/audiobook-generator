import React, { useMemo } from "react";
import { Script } from "../actions/script";
import { Voice } from "../actions/voices";

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

  script.forEach((segment) => {
    const characterName = segment.speaker.names[0];
    // Skip segments with no character name
    if (
      characterName &&
      characterName.trim() &&
      !characterMap.has(characterName)
    ) {
      characterMap.set(characterName, segment.voice_name);
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

  if (characterMappings.length === 0) {
    return (
      <div className="mb-6 p-4 bg-base-100 rounded border">
        <h3 className="text-lg font-semibold mb-2">
          Character Voice Assignments
        </h3>
        <p className="text-sm text-base-content/70">
          No characters found in the script.
        </p>
      </div>
    );
  }

  return (
    <div className="mb-6 p-4 bg-base-100 rounded">
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
