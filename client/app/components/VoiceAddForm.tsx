"use client";

import React from "react";
import { useState } from "react";

import { AgeEnum, GenderEnum } from "../types";

import { addVoice, type Age, type Gender } from "../actions/voices";
import { handleRevalidateTag } from "../actions/revalidate";

export default function VoiceAddForm() {
  const [name, setName] = useState("");
  const [age, setAge] = useState<Age | "">("");
  const [gender, setGender] = useState<Gender | "">("");
  const [audioTranscript, setAudioTranscript] = useState("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAudioFile(e.target.files[0]);
    }
  };

  async function handleAddVoice() {
    if (name && age && gender && audioTranscript && audioFile) {
      setIsSubmitting(true);
      try {
        await addVoice({
          name,
          age: age as Age,
          gender: gender as Gender,
          audio_transcript: audioTranscript,
          audio_file: audioFile,
        });

        setName("");
        setAge("");
        setGender("");
        setAudioTranscript("");
        setAudioFile(null);

        const fileInput = document.getElementById(
          "audio-file-input"
        ) as HTMLInputElement;
        if (fileInput) {
          fileInput.value = "";
        }

        await handleRevalidateTag("voices");
      } catch (error) {
        console.error("Failed to add voice:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  const isFormValid = name && age && gender && audioTranscript && audioFile;

  return (
    <div className="flex flex-col gap-2 bg-gray-50 p-4 rounded">
      <label htmlFor="name-input" className="font-medium">
        Name
      </label>
      <input
        id="name-input"
        name="name"
        type="text"
        className="bg-gray-200 p-2 rounded"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter voice name"
        required
      />

      <div className="grid grid-cols-2 gap-2">
        <div className="flex flex-col gap-2">
          <label htmlFor="age-select" className="font-medium">
            Age
          </label>
          <select
            id="age-select"
            name="age"
            className="bg-gray-200 p-2 rounded"
            value={age}
            onChange={(e) => setAge(e.target.value as Age)}
            required
          >
            <option value="">Select age</option>
            {AgeEnum.options.map((ageValue) => (
              <option key={ageValue} value={ageValue}>
                {ageValue.charAt(0).toUpperCase() + ageValue.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-2">
          <label htmlFor="gender-select" className="font-medium">
            Gender
          </label>
          <select
            id="gender-select"
            name="gender"
            className="bg-gray-200 p-2 rounded"
            value={gender}
            onChange={(e) => setGender(e.target.value as Gender)}
            required
          >
            <option value="">Select gender</option>
            {GenderEnum.options.map((genderValue) => (
              <option key={genderValue} value={genderValue}>
                {genderValue.charAt(0).toUpperCase() + genderValue.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <label htmlFor="audio-file-input" className="font-medium">
        Audio File
      </label>
      <input
        id="audio-file-input"
        name="audio_file"
        type="file"
        accept="audio/*"
        onChange={handleFileChange}
        className="bg-gray-200 p-2 rounded"
        required
      />

      <label htmlFor="transcript-input" className="font-medium">
        Audio Transcript
      </label>
      <textarea
        id="transcript-input"
        name="audio_transcript"
        className="bg-gray-200 p-2 rounded"
        value={audioTranscript}
        onChange={(e) => setAudioTranscript(e.target.value)}
        placeholder="Enter the transcript of the audio file"
        rows={3}
        required
      />

      <button
        disabled={!isFormValid || isSubmitting}
        onClick={async () => {
          await handleAddVoice();
        }}
        className="bg-blue-500 text-white p-2 rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {isSubmitting ? "Adding Voice..." : "Add Voice"}
      </button>
    </div>
  );
}
