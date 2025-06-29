import React, { useMemo, useState } from "react";
import { Script } from "@/app/actions/script";
import { Voice, Age, Gender } from "@/app/actions/voices";
import { ManualCharacter } from "@/app/types";
import { AgeEnum, GenderEnum } from "@/app/types";

interface CharacterVoiceMappingProps {
  script: Script;
  voices: Voice[];
  manualCharacters: ManualCharacter[];
  onCharacterVoiceChange: (characterName: string, voiceName: string) => void;
  onAddCharacter: (character: ManualCharacter) => void;
}

interface CharacterMapping {
  characterName: string;
  currentVoice: string;
}

function extractCharacterMappings(
  script: Script,
  manualCharacters: ManualCharacter[]
): CharacterMapping[] {
  const characterMap = new Map<string, string>();

  // Use speakers array with voice_name directly from speaker details
  script.speakers.forEach((speaker) => {
    const characterName = speaker.names[0];
    if (characterName && characterName.trim()) {
      const voiceName = speaker.voice_name || "";
      characterMap.set(characterName, voiceName);
    }
  });

  manualCharacters.forEach((character) => {
    if (!characterMap.has(character.name)) {
      characterMap.set(character.name, "");
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
  manualCharacters,
  onCharacterVoiceChange,
  onAddCharacter,
}: CharacterVoiceMappingProps) {
  const [newCharacterName, setNewCharacterName] = useState("");
  const [newCharacterAge, setNewCharacterAge] = useState<Age | "">("");
  const [newCharacterGender, setNewCharacterGender] = useState<Gender | "">("");

  const characterMappings = useMemo(
    () => extractCharacterMappings(script, manualCharacters),
    [script, manualCharacters]
  );

  const handleAddCharacter = () => {
    if (newCharacterName.trim() && newCharacterAge && newCharacterGender) {
      const character: ManualCharacter = {
        name: newCharacterName.trim(),
        age: newCharacterAge,
        gender: newCharacterGender,
      };
      onAddCharacter(character);
      setNewCharacterName("");
      setNewCharacterAge("");
      setNewCharacterGender("");
    }
  };

  const isFormValid =
    newCharacterName.trim() && newCharacterAge && newCharacterGender;

  return (
    <div className="bg-base-200 p-4 rounded">
      {/* Add Character Form */}
      <div className="mb-4 p-3 bg-base-300 rounded">
        <h3 className="text-sm font-medium mb-3">Add New Character</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
          <input
            type="text"
            placeholder="Character name"
            value={newCharacterName}
            onChange={(e) => setNewCharacterName(e.target.value)}
            className="input input-sm input-bordered"
          />
          <select
            value={newCharacterAge}
            onChange={(e) => setNewCharacterAge(e.target.value as Age)}
            className="select select-sm select-bordered"
          >
            <option value="">Select age</option>
            {AgeEnum.options.map((age) => (
              <option key={age} value={age}>
                {age}
              </option>
            ))}
          </select>
          <select
            value={newCharacterGender}
            onChange={(e) => setNewCharacterGender(e.target.value as Gender)}
            className="select select-sm select-bordered"
          >
            <option value="">Select gender</option>
            {GenderEnum.options.map((gender) => (
              <option key={gender} value={gender}>
                {gender}
              </option>
            ))}
          </select>
          <button
            onClick={handleAddCharacter}
            disabled={!isFormValid}
            className="btn btn-sm btn-primary"
          >
            Add
          </button>
        </div>
      </div>

      {/* Character Voice Mappings */}
      <div className="max-h-[14rem] overflow-y-scroll">
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
    </div>
  );
}
