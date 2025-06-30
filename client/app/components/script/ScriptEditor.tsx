import React, { useState, useEffect } from "react";

import { Script, updateScript } from "@/app/actions/script";
import { Voice, Age, Gender } from "@/app/actions/voices";
import { ManualCharacter } from "@/app/types";
import Tip from "@/app/components/ui/Tip";
import CharacterVoiceMapping from "./CharacterVoiceMapping";

interface ScriptEditorProps {
  script: Script;
  voices: Voice[];
}

export default function ScriptEditor({ script, voices }: ScriptEditorProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    setEditingScript(script);
  }, [script]);

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
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
      await updateScript({ script: scriptToSave });
      setSuccess("Saved");
      setTimeout(() => setSuccess(null), 2000);
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

  const handleCharacterVoiceChange = (
    characterName: string,
    voiceName: string
  ) => {
    clearMessages();
    const selectedVoice = voices.find((voice) => voice.name === voiceName);
    if (selectedVoice) {
      // Update the speaker's voice information
      const updatedSpeakers = editingScript.speakers.map((speaker) => {
        if (speaker.names.includes(characterName)) {
          return {
            ...speaker,
            voice_name: selectedVoice.name,
            age: selectedVoice.age,
            gender: selectedVoice.gender,
            audio_path: selectedVoice.audio_path,
            audio_transcript: selectedVoice.audio_transcript,
          };
        }
        return speaker;
      });

      const updatedScript = {
        ...editingScript,
        speakers: updatedSpeakers,
      };

      setEditingScript(updatedScript);
      debouncedAutoSave(updatedScript);
    }
  };

  const handleAddCharacter = (character: ManualCharacter) => {
    clearMessages();

    // Check if character already exists in script speakers
    const existingSpeaker = editingScript.speakers.find((speaker) =>
      speaker.names.includes(character.name)
    );

    if (!existingSpeaker) {
      // Add character to script speakers array
      const newSpeaker = {
        names: [character.name],
        age: character.age,
        gender: character.gender,
        voice_name: "",
        audio_path: "",
        audio_transcript: "",
      };

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

    // Find the character in script speakers
    let characterAge: Age = "middle-aged";
    let characterGender: Gender = "male";
    let characterVoice = "";

    // Check existing script speakers for this character
    const existingSpeaker = editingScript.speakers.find((speaker) =>
      speaker.names.includes(characterName)
    );
    if (existingSpeaker) {
      characterAge = existingSpeaker.age;
      characterGender = existingSpeaker.gender;
      characterVoice = existingSpeaker.voice_name;
    }

    // Update the segment's speaker_alias
    updatedSegments[segmentIndex] = {
      ...updatedSegments[segmentIndex],
      speaker_alias: characterName,
    };

    // Update or add speaker in speakers array
    const updatedSpeakers = [...editingScript.speakers];
    const speakerIndex = updatedSpeakers.findIndex((speaker) =>
      speaker.names.includes(characterName)
    );

    if (speakerIndex >= 0) {
      // Update existing speaker
      updatedSpeakers[speakerIndex] = {
        ...updatedSpeakers[speakerIndex],
        names: [characterName],
        age: characterAge,
        gender: characterGender,
        voice_name: characterVoice,
      };
    } else {
      // Add new speaker
      const selectedVoice = voices.find((v) => v.name === characterVoice);
      updatedSpeakers.push({
        names: [characterName],
        age: characterAge,
        gender: characterGender,
        voice_name: characterVoice,
        audio_path: selectedVoice?.audio_path || "",
        audio_transcript: selectedVoice?.audio_transcript || "",
      });
    }

    const updatedScript = {
      ...editingScript,
      segments: updatedSegments,
      speakers: updatedSpeakers,
    };

    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  // Get all available characters from script speakers
  const getAllCharacters = () => {
    const scriptCharacters = new Set<string>();
    editingScript.speakers.forEach((speaker) => {
      speaker.names.forEach((name) => {
        if (name && name.trim()) {
          scriptCharacters.add(name);
        }
      });
    });

    return Array.from(scriptCharacters).sort();
  };

  const availableCharacters = getAllCharacters();

  return (
    <div className="flex flex-col gap-4">
      {(error || success || isSaving) && (
        <div className="mb-4">
          {isSaving && (
            <span className="flex items-center loading loading-spinner loading-sm"></span>
          )}
          {error && <Tip variant="warning">{error}</Tip>}
        </div>
      )}

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
