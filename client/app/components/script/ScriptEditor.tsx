"use client";

import React, { useState, useEffect, useMemo } from "react";

import { Script, updateScript } from "@/app/actions/script";
import { Voice } from "@/app/actions/voices";
import { ManualCharacter } from "@/app/types";
import Tip from "@/app/components/ui/Tip";
import CharacterVoiceMapping from "./CharacterVoiceMapping";
import AudioPlayer from "@/app/components/audio/AudioPlayer";
import { getSegmentAudioUrl } from "@/app/actions/segments";

interface ScriptEditorProps {
  script: Script;
  voices: Voice[];
  chapterName: string;
  audioSegmentIds: string[];
}

export default function ScriptEditor({
  script,
  voices,
  chapterName,
  audioSegmentIds,
}: ScriptEditorProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);

  useEffect(() => {
    setEditingScript(script);
  }, [script]);

  const playableSegmentIds = useMemo(
    () => new Set(audioSegmentIds),
    [audioSegmentIds]
  );

  const clearMessages = () => {};

  const autoSave = async (scriptToSave: Script) => {
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
    } catch (error) {
      console.error("Error updating script:", error);
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
    character: {
      names: [characterName],
      age: voice?.age || existingAge,
      gender: voice?.gender || existingGender,
    },
    voice: {
      name: voice?.name || "",
      age: voice?.age || existingAge,
      gender: voice?.gender || existingGender,
      audio_path: voice?.audio_path || "",
      audio_transcript: voice?.audio_transcript || "",
    },
  });

  const handleCharacterVoiceChange = (
    characterName: string,
    voiceName: string
  ) => {
    clearMessages();
    const selectedVoice =
      voices.find((voice) => voice.name === voiceName) || null;

    const updatedSpeakers = editingScript.speakers.map((speaker) =>
      speaker.character.names.includes(characterName)
        ? createSpeakerFromVoice(
            characterName,
            selectedVoice,
            speaker.character.age,
            speaker.character.gender
          )
        : speaker
    );

    const updatedScript = { ...editingScript, speakers: updatedSpeakers };
    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  const handleAddCharacter = (character: ManualCharacter) => {
    clearMessages();

    const existingSpeaker = editingScript.speakers.find((speaker) =>
      speaker.character.names.includes(character.name)
    );

    if (!existingSpeaker) {
      const newSpeaker = createSpeakerFromVoice(
        character.name,
        null,
        character.age,
        character.gender
      );

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
      .flatMap((speaker) => speaker.character.names)
      .filter((name) => name?.trim())
      .sort();

  const availableCharacters = getAllCharacters();

  return (
    <div className="flex flex-col gap-4">
      <Tip>
        Edit the script text, choose voices for characters, and save changes.
      </Tip>

      <CharacterVoiceMapping
        script={editingScript}
        voices={voices}
        onCharacterVoiceChange={handleCharacterVoiceChange}
        onAddCharacter={handleAddCharacter}
      />

      <div className="h-[28rem] overflow-y-scroll bg-base-200 p-4 rounded">
        {editingScript.segments.map((scriptSegment, index) => {
          const speaker = editingScript.speakers.find((s) =>
            s.character.names.includes(scriptSegment.speaker_alias)
          );
          const characterName =
            speaker?.character.names[0] || scriptSegment.speaker_alias;
          const voiceName = speaker?.voice.name || "";
          const segmentId = scriptSegment.id as string | undefined;
          const hasAudio = segmentId
            ? playableSegmentIds.has(segmentId)
            : false;

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
                      className="select select-sm select-bordered min-w-[120px]"
                    >
                      {availableCharacters.map((char) => (
                        <option key={char} value={char}>
                          {char}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm">{voiceName}</span>
                    {hasAudio ? (
                      <SegmentAudioLoader
                        chapterName={chapterName}
                        segmentId={segmentId as string}
                      />
                    ) : null}
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

function SegmentAudioLoader({
  chapterName,
  segmentId,
}: {
  chapterName: string;
  segmentId: string;
}) {
  const [src, setSrc] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const load = async () => {
    if (src || loading) return;
    setLoading(true);
    try {
      const url = await getSegmentAudioUrl(chapterName, segmentId);
      setSrc(url);
    } finally {
      setLoading(false);
    }
  };

  return src ? (
    <AudioPlayer src={src} autoPlay />
  ) : (
    <button
      onClick={load}
      disabled={loading}
      className="btn btn-success btn-outline btn-sm"
    >
      {loading ? "Loading..." : "Play"}
    </button>
  );
}
