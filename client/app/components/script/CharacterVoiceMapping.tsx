import React, { useMemo, useState } from "react";
import { Script } from "@/app/actions/script";
import { Voice } from "@/app/actions/voices";
import { ManualCharacter } from "@/app/types";
import AddCharacterModal from "./AddCharacterModal";

interface CharacterVoiceMappingProps {
  script: Script;
  voices: Voice[];
  onCharacterVoiceChange: (characterName: string, voiceName: string) => void;
  onAddCharacter: (character: ManualCharacter) => void;
}

interface CharacterMapping {
  characterName: string;
  currentVoice: string;
}

function extractCharacterMappings(script: Script): CharacterMapping[] {
  const characterMap = new Map<string, string>();

  // Use speakers array with voice_name directly from speaker details
  script.speakers.forEach((speaker) => {
    const characterName = speaker.names[0];
    if (characterName && characterName.trim()) {
      const voiceName = speaker.voice_name || "";
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
  onAddCharacter,
}: CharacterVoiceMappingProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const characterMappings = useMemo(
    () => extractCharacterMappings(script),
    [script]
  );

  return (
    <div className="bg-base-200 p-4 rounded">
      <div className="max-h-[14rem] overflow-y-scroll mb-4">
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
                <option value="">Select voice</option>
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

      <button onClick={() => setIsModalOpen(true)} className="btn w-full">
        Add New Character
      </button>

      <AddCharacterModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAddCharacter={onAddCharacter}
      />
    </div>
  );
}
