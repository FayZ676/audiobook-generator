import React, { useState, useEffect, useCallback } from "react";

import { Script, updateScript } from "../actions/script";
import { Voice, Age, Gender } from "../actions/voices";
import { ManualCharacter } from "../types";
import Tip from "./Tip";
import CharacterVoiceMapping from "./CharacterVoiceMapping";

interface ScriptEditorProps {
  script: Script;
  voices: Voice[];
}

export default function ScriptEditor({ script, voices }: ScriptEditorProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);
  const [manualCharacters, setManualCharacters] = useState<ManualCharacter[]>([]);
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

  const autoSave = useCallback(async (scriptToSave: Script) => {
    if (scriptToSave.length === 0) {
      setError("Script cannot be empty");
      return;
    }

    const hasEmptyText = scriptToSave.some((segment) => !segment.text.trim());
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
  }, []);

  const debouncedAutoSave = useCallback(
    (() => {
      let timeoutId: NodeJS.Timeout;
      return (scriptToSave: Script) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => autoSave(scriptToSave), 1000);
      };
    })(),
    [autoSave]
  );

  const handleTextChange = (index: number, newText: string) => {
    clearMessages();
    const updatedScript = [...editingScript];
    updatedScript[index] = { ...updatedScript[index], text: newText };
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
      const updatedScript = editingScript.map((segment) => {
        // Update all segments where this character speaks
        const segmentCharacterName = segment.speaker.names[0];
        if (segmentCharacterName && segmentCharacterName === characterName) {
          return {
            ...segment,
            voice_name: selectedVoice.name,
            speaker: {
              ...segment.speaker,
              // Keep the original character name, but update voice-related fields if needed
              names: segment.speaker.names,
            },
          };
        }
        return segment;
      });
      setEditingScript(updatedScript);
      debouncedAutoSave(updatedScript);
    }
  };

  const handleAddCharacter = (character: ManualCharacter) => {
    // Check if character already exists
    const existingCharacter = manualCharacters.find(c => c.name === character.name);
    if (!existingCharacter) {
      setManualCharacters(prev => [...prev, character]);
    }
  };

  const handleSegmentCharacterChange = (
    segmentIndex: number,
    characterName: string
  ) => {
    clearMessages();
    const updatedScript = [...editingScript];
    
    // Find the character (either from script or manual characters)
    let characterAge: Age = "middle-aged";
    let characterGender: Gender = "male";
    
    // First check existing script segments for this character
    const existingSegment = editingScript.find(
      seg => seg.speaker.names[0] === characterName
    );
    if (existingSegment) {
      characterAge = existingSegment.speaker.age;
      characterGender = existingSegment.speaker.gender;
    } else {
      // Check manual characters
      const manualCharacter = manualCharacters.find(c => c.name === characterName);
      if (manualCharacter) {
        characterAge = manualCharacter.age;
        characterGender = manualCharacter.gender;
      }
    }

    updatedScript[segmentIndex] = {
      ...updatedScript[segmentIndex],
      speaker: {
        names: [characterName],
        age: characterAge,
        gender: characterGender,
      },
      // Keep existing voice or reset if character doesn't have one assigned
      voice_name: updatedScript[segmentIndex].voice_name,
    };
    
    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  // Get all available characters (from script + manual)
  const getAllCharacters = () => {
    const scriptCharacters = new Set<string>();
    editingScript.forEach(segment => {
      const characterName = segment.speaker.names[0];
      if (characterName && characterName.trim()) {
        scriptCharacters.add(characterName);
      }
    });
    
    const allCharacters = Array.from(scriptCharacters);
    manualCharacters.forEach(character => {
      if (!allCharacters.includes(character.name)) {
        allCharacters.push(character.name);
      }
    });
    
    return allCharacters.sort();
  };

  return (
    <div className="flex flex-col gap-4">
      {(error || success || isSaving) && (
        <div className="mb-4 flex items-center gap-2">
          {isSaving && (
            <span className="loading loading-spinner loading-sm"></span>
          )}
          {error && <Tip variant="warning">{error}</Tip>}
        </div>
      )}

      <CharacterVoiceMapping
        script={editingScript}
        voices={voices}
        manualCharacters={manualCharacters}
        onCharacterVoiceChange={handleCharacterVoiceChange}
        onAddCharacter={handleAddCharacter}
      />

      <div className="h-[28rem] overflow-y-scroll bg-base-200 p-4 rounded">
        {editingScript.map((scriptSegment, index) => {
          const characterName = scriptSegment.speaker.names[0] || "Unknown";
          const availableCharacters = getAllCharacters();
          
          return (
            <div key={index} className="mb-4">
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-base-content/70">Character:</span>
                    <select
                      value={characterName}
                      onChange={(e) => handleSegmentCharacterChange(index, e.target.value)}
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
                    Voice: {scriptSegment.voice_name || "Not assigned"}
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
