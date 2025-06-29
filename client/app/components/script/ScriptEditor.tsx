import React, { useState, useEffect } from "react";

import { Script, updateScript } from "../../actions/script";
import { Voice } from "../../actions/voices";
import Tip from "../ui/Tip";
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

    const hasEmptyText = scriptToSave.segments.some((segment) => !segment.text.trim());
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
      // Update the voices mapping
      const updatedVoices = { ...editingScript.voices, [characterName]: selectedVoice.name };
      
      // Update segments to use the new voice
      const updatedSegments = editingScript.segments.map((segment) => {
        if (segment.speaker_alias === characterName) {
          return {
            ...segment,
            voice_name: selectedVoice.name,
          };
        }
        return segment;
      });
      
      const updatedScript = {
        ...editingScript,
        segments: updatedSegments,
        voices: updatedVoices,
      };
      
      setEditingScript(updatedScript);
      debouncedAutoSave(updatedScript);
    }
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
        onCharacterVoiceChange={handleCharacterVoiceChange}
      />

      <div className="h-[28rem] overflow-y-scroll bg-base-200 p-4 rounded">
        {editingScript.segments.map((scriptSegment, index) => {
          // Find speaker details for this segment
          const speaker = editingScript.speakers.find(s => 
            s.names.includes(scriptSegment.speaker_alias)
          );
          const characterName = speaker?.names[0] || scriptSegment.speaker_alias;
          
          return (
            <div key={index} className="mb-4">
              <div className="flex flex-col gap-2">
                <div className="flex justify-between">
                  <div className="text-sm font-medium">{characterName}</div>
                  <div className="text-xs text-base-content/70 px-3">
                    {scriptSegment.voice_name}
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
