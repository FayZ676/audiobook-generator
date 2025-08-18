"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import { RotateCw, LoaderCircle } from "lucide-react";

import { Script, updateScript } from "@/app/actions/script";
import { Voice } from "@/app/actions/voices";
import { regenerateSegment } from "@/app/actions/segments";
import { ManualCharacter, AudioSegmentData } from "@/app/types";

import CharacterVoiceMappingClient from "@/app/components/script/CharacterVoiceMappingClient";
import AudioPlayer from "@/app/components/audio/AudioPlayer";
import NarrationAudio from "@/app/components/narration/NarrationAudio";
import TextArea from "@/app/components/ui/TextArea";

interface ScriptEditorProps {
  script: Script;
  voicesPromise: Promise<Voice[]>;
  chapterName: string;
  processingSegmentIds?: string[];
  audioSegmentData: AudioSegmentData;
  narrationUrl?: string | null;
}

export default function ScriptEditor({
  script,
  voicesPromise,
  chapterName,
  processingSegmentIds,
  audioSegmentData,
  narrationUrl,
}: ScriptEditorProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);
  const [regenerating, setRegenerating] = useState<Record<string, boolean>>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  useEffect(() => {
    setEditingScript(script);
    setHasUnsavedChanges(false);
  }, [script]);

  const processingSet = useMemo(
    () => new Set(processingSegmentIds || []),
    [processingSegmentIds]
  );
  const playableSet = useMemo(
    () => new Set(audioSegmentData.ids || []),
    [audioSegmentData.ids]
  );

  const isAnySegmentRegenerating = useMemo(() => {
    return processingSet.size > 0 || Object.values(regenerating).some(Boolean);
  }, [processingSet, regenerating]);

  const clearMessages = () => {};

  const saveScript = async (scriptToSave: Script) => {
    if (scriptToSave.segments.length === 0) {
      return;
    }

    const hasEmptyText = scriptToSave.segments.some(
      (segment) => !segment.text.trim()
    );
    if (hasEmptyText) {
      return;
    }

    clearMessages();

    try {
      await updateScript({ script: scriptToSave, chapterName });
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error("Error updating script:", error);
    }
  };

  const handleTextChange = (index: number, newText: string) => {
    clearMessages();
    const updatedSegments = [...editingScript.segments];
    updatedSegments[index] = { ...updatedSegments[index], text: newText };
    const updatedScript = { ...editingScript, segments: updatedSegments };
    setEditingScript(updatedScript);
    setHasUnsavedChanges(true);
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
    saveScript(updatedScript);
  };

  const getAllCharacters = () =>
    editingScript.speakers
      .flatMap((speaker) => speaker.character.names)
      .filter((name) => name?.trim())
      .sort();

  const availableCharacters = getAllCharacters();

  const handleRegenerate = async (segmentId: string) => {
    try {
      setRegenerating((prev) => ({ ...prev, [segmentId]: true }));
      await regenerateSegment(chapterName, segmentId);
    } catch (e) {
      console.error("Failed to regenerate segment", e);
    } finally {
      // keep local true until pusher refresh clears via processingSegmentIds update
      // but safe to set false as isRegenerating is union with processingSet
      setRegenerating((prev) => ({ ...prev, [segmentId]: false }));
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <Suspense fallback={<div>Loading character voice mapping...</div>}>
        <CharacterVoiceMappingClient
          script={editingScript}
          voicesPromise={voicesPromise}
          onScriptUpdate={(updatedScript: Script) => {
            setEditingScript(updatedScript);
            saveScript(updatedScript);
          }}
          onAddCharacter={(character: ManualCharacter) => {
            const exists = editingScript.speakers.find((s) =>
              s.character.names.includes(character.name)
            );
            if (!exists) {
              const newSpeaker = {
                character: {
                  names: [character.name],
                  age: character.age,
                  gender: character.gender,
                },
                voice: {
                  name: "",
                  age: character.age,
                  gender: character.gender,
                  audio_path: "",
                  audio_transcript: "",
                },
              };
              const updatedScript = {
                ...editingScript,
                speakers: [...editingScript.speakers, newSpeaker],
              };
              setEditingScript(updatedScript);
              saveScript(updatedScript);
            }
          }}
        />
      </Suspense>

      <div className="flex flex-col gap-4 max-h-[32rem] overflow-y-scroll bg-base-200 p-4 rounded">
        {narrationUrl && (
          <NarrationAudio
            narrationUrl={narrationUrl}
            disabled={isAnySegmentRegenerating}
          />
        )}
        {editingScript.segments.map((scriptSegment, index) => {
          const speaker = editingScript.speakers.find((s) =>
            s.character.names.includes(scriptSegment.speaker_alias)
          );
          const characterName =
            speaker?.character.names[0] || scriptSegment.speaker_alias;
          const segmentId = scriptSegment.id as string | undefined;
          const segmentUrl = segmentId
            ? audioSegmentData.urls[segmentId]
            : undefined;
          const hasAudio = segmentId
            ? playableSet.has(segmentId) || !!segmentUrl
            : false;
          const isRegenerating = segmentId
            ? !!regenerating[segmentId] || processingSet.has(segmentId)
            : false;

          return (
            <div
              key={index}
              className={`mb-4 ${isRegenerating ? "opacity-80" : ""}`}
            >
              <div className="flex flex-col gap-2">
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={characterName}
                    onChange={(e) =>
                      handleSegmentCharacterChange(index, e.target.value)
                    }
                    className="select select-sm min-w-[120px] text-gray-500 italic"
                    disabled={isAnySegmentRegenerating}
                  >
                    {availableCharacters.map((char) => (
                      <option key={char} value={char}>
                        {char}
                      </option>
                    ))}
                  </select>
                  <div className="ml-auto flex items-center gap-3">
                    {segmentId && hasAudio && (
                      <div className="flex items-center gap-2">
                        {segmentUrl && (
                          <AudioPlayer
                            src={segmentUrl}
                            disabled={isAnySegmentRegenerating}
                          />
                        )}
                        <button
                          className="btn btn-sm btn-outline btn-info"
                          title="Regenerate segment"
                          onClick={() => handleRegenerate(segmentId)}
                          disabled={isAnySegmentRegenerating}
                        >
                          {isRegenerating ? (
                            <LoaderCircle size={16} className="animate-spin" />
                          ) : (
                            <RotateCw size={16} />
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex-1">
                  <TextArea
                    value={scriptSegment.text}
                    onChange={(newText) => handleTextChange(index, newText)}
                    onBlur={() => {
                      if (hasUnsavedChanges) {
                        saveScript(editingScript);
                      }
                    }}
                    placeholder="Enter script text..."
                    disabled={isAnySegmentRegenerating}
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
