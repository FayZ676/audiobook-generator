"use client";

import React, { use, useState, useCallback } from "react";
import { Script } from "@/app/actions/script";
import { Voice } from "@/app/actions/voices";
import { ManualCharacter } from "@/app/types";
import AddCharacterModal from "./AddCharacterModal";

interface CharacterVoiceMappingClientProps {
  script: Script;
  voicesPromise: Promise<Voice[]>;
  onScriptUpdate: (updatedScript: Script) => void;
  onAddCharacter: (character: ManualCharacter) => void;
}

interface CharacterMapping {
  characterName: string;
  currentVoice: string;
}

function extractCharacterMappings(script: Script): CharacterMapping[] {
  return script.speakers.map((speaker) => ({
    characterName: speaker.character.names[0],
    currentVoice: speaker.voice.name,
  }));
}

export default function CharacterVoiceMappingClient({
  script,
  voicesPromise,
  onScriptUpdate,
  onAddCharacter,
}: CharacterVoiceMappingClientProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const voices = use(voicesPromise);

  const handleCharacterVoiceChange = useCallback(
    (characterName: string, voiceName: string) => {
      const voice = voices.find((v) => v.name === voiceName);

      if (!voice) {
        console.error(`Voice "${voiceName}" not found in available voices`);
        return;
      }

      const updatedSpeakers = script.speakers.map((speaker) => {
        if (speaker.character.names.includes(characterName)) {
          return {
            ...speaker,
            voice: {
              name: voice.name,
              age: voice.age,
              gender: voice.gender,
              audio_path: voice.audio_path,
              audio_transcript: voice.audio_transcript,
            },
          };
        }
        return speaker;
      });

      const updatedScript = { ...script, speakers: updatedSpeakers };
      onScriptUpdate(updatedScript);
    },
    [voices, script, onScriptUpdate]
  );

  return (
    <div className="bg-base-200 p-4 rounded">
      <div className="max-h-[14rem] overflow-y-scroll mb-4 space-y-2">
        {extractCharacterMappings(script).map((mapping) => (
          <div key={mapping.characterName} className="grid grid-cols-2 gap-2 ">
            <span className="truncate">{mapping.characterName}</span>
            <select
              value={mapping.currentVoice}
              onChange={(e) =>
                handleCharacterVoiceChange(
                  mapping.characterName,
                  e.target.value
                )
              }
              className="select select-sm select-bordered ml-auto"
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
