import React, { useState, useEffect } from "react";

import { Script, updateScript } from "@/app/actions/script";
import { Voice } from "@/app/actions/voices";
import { ManualCharacter } from "@/app/types";
import Tip from "@/app/components/ui/Tip";
import CharacterVoiceMapping from "./CharacterVoiceMapping";

interface ScriptEditorProps {
  script: Script;
  voices: Voice[];
  filename?: string;
}

export default function ScriptEditor({ script, voices, filename }: ScriptEditorProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setEditingScript(script);
  }, [script]);

  const clearMessages = () => {
    setError(null);
  };

  const autoSave = async (scriptToSave: Script) => {
    if (scriptToSave.segments.length === 0) {
      setError("Script cannot be empty");
      return;
    }

    const hasEmptyText = scriptToSave.segments.some(
      (segment) => !segment.text.trim()
    );
    if (hasEmptyText) {
      setError("All script segments must have text");
      return;
    }

    setIsSaving(true);
    clearMessages();

    try {
      if (filename) {
        await updateScript(filename, scriptToSave);
      } else {
        // Fallback for backward compatibility
        await updateScript("default", scriptToSave);
      }
    } catch (error) {
      console.error("Error updating script:", error);
      setError("Failed to save script");
    } finally {
      setIsSaving(false);
    }
  };

  const debouncedAutoSave = (() => {
    let timeoutId: NodeJS.Timeout;
    return (scriptToSave: Script) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => autoSave(scriptToSave), 1000);
    };
  })();

  const handleTextChange = (index: number, newText: string) => {
    clearMessages();
    const updatedSegments = [...editingScript.segments];
    updatedSegments[index] = { ...updatedSegments[index], text: newText };
    const updatedScript = { ...editingScript, segments: updatedSegments };
    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  const createSpeakerFromVoice = (
    characterName: string, 
    voice: Voice | null, 
    existingAge: "young" | "middle-aged" | "old", 
    existingGender: "male" | "female"
  ) => ({
    names: [characterName],
    age: voice?.age || existingAge,
    gender: voice?.gender || existingGender,
    voice_name: voice?.name || "",
    audio_path: voice?.audio_path || "",
    audio_transcript: voice?.audio_transcript || "",
  });

  const handleCharacterVoiceChange = (
    characterName: string,
    voiceName: string
  ) => {
    clearMessages();
    const selectedVoice = voices.find((voice) => voice.name === voiceName) || null;
    
    const updatedSpeakers = editingScript.speakers.map((speaker) =>
      speaker.names.includes(characterName)
        ? createSpeakerFromVoice(characterName, selectedVoice, speaker.age, speaker.gender)
        : speaker
    );

    const updatedScript = { ...editingScript, speakers: updatedSpeakers };
    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  const handleAddCharacter = (character: ManualCharacter) => {
    clearMessages();

    const existingSpeaker = editingScript.speakers.find((speaker) =>
      speaker.names.includes(character.name)
    );

    if (!existingSpeaker) {
      const newSpeaker = createSpeakerFromVoice(character.name, null, character.age, character.gender);

      const updatedScript = {
        ...editingScript,
        speakers: [...editingScript.speakers, newSpeaker],
      };

      setEditingScript(updatedScript);
      debouncedAutoSave(updatedScript);
    }
  };

  const handleSegmentCharacterChange = (
    segmentIndex: number,
    characterName: string
  ) => {
    clearMessages();
    const updatedSegments = [...editingScript.segments];
    updatedSegments[segmentIndex] = {
      ...updatedSegments[segmentIndex],
      speaker_alias: characterName,
    };

    const updatedScript = { ...editingScript, segments: updatedSegments };
    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  const getAllCharacters = () =>
    editingScript.speakers
      .flatMap((speaker) => speaker.names)
      .filter((name) => name?.trim())
      .sort();

  const availableCharacters = getAllCharacters();

  return (
    <div className="flex flex-col gap-4">
      <div className="h-8 flex items-center">
        {isSaving && (
          <span className="flex items-center loading loading-spinner loading-sm"></span>
        )}
        {error && <Tip variant="warning">{error}</Tip>}
      </div>

      <CharacterVoiceMapping
        script={editingScript}
        voices={voices}
        onCharacterVoiceChange={handleCharacterVoiceChange}
        onAddCharacter={handleAddCharacter}
      />

      <div className="h-[28rem] overflow-y-scroll bg-base-200 p-4 rounded">
        {editingScript.segments.map((scriptSegment, index) => {
          const speaker = editingScript.speakers.find((s) =>
            s.names.includes(scriptSegment.speaker_alias)
          );
          const characterName =
            speaker?.names[0] || scriptSegment.speaker_alias;
          const voiceName = speaker?.voice_name || "";

          return (
            <div key={index} className="mb-4">
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <select
                      value={characterName}
                      onChange={(e) =>
                        handleSegmentCharacterChange(index, e.target.value)
                      }
                      className="select select-xs select-bordered min-w-[120px]"
                    >
                      {availableCharacters.map((char) => (
                        <option key={char} value={char}>
                          {char}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="text-xs text-base-content/70 px-3">
                    {voiceName}
                  </div>
                </div>
                <div className="flex-1">
                  <textarea
                    value={scriptSegment.text}
                    onChange={(e) => handleTextChange(index, e.target.value)}
                    className="textarea textarea-bordered w-full min-h-[80px]"
                    rows={3}
                    placeholder="Enter script text..."
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
