"use client";

import React from "react";
import { useState, useRef } from "react";

import { AgeEnum, GenderEnum } from "../../types";

import { addVoice, type Age, type Gender } from "../../actions/voices";
import Tip from "../ui/Tip";
import AudioRecorder from "../AudioRecorder";

interface VoiceAddModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function VoiceAddModal({ isOpen, onClose }: VoiceAddModalProps) {
  const [name, setName] = useState("");
  const [age, setAge] = useState<Age | "">("");
  const [gender, setGender] = useState<Gender | "">("");
  const [audioTranscript, setAudioTranscript] = useState("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [audioInputMode, setAudioInputMode] = useState<"upload" | "record">(
    "upload"
  );
  const modalRef = useRef<HTMLDialogElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAudioFile(e.target.files[0]);
    }
  };

  const handleRecordingComplete = (recordedFile: File) => {
    setAudioFile(recordedFile);
  };

  const handleAudioInputModeChange = (mode: "upload" | "record") => {
    setAudioInputMode(mode);
    setAudioFile(null);

    if (mode === "record") {
      const fileInput = document.getElementById(
        "audio-file-input"
      ) as HTMLInputElement;
      if (fileInput) {
        fileInput.value = "";
      }
    }

    modalRef.current?.showModal();
  };

  const closeModal = () => {
    modalRef.current?.close();
  };

  const handleModalFileSelect = () => {
    closeModal();
  };

  const handleModalRecordingComplete = (recordedFile: File) => {
    setAudioFile(recordedFile);
    closeModal();
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

        setAudioInputMode("upload");

        onClose();
      } catch (error) {
        console.error("Failed to add voice:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  const handleClose = () => {
    onClose();
  };

  const isFormValid = name && age && gender && audioTranscript && audioFile;

  return (
    <div className={`modal ${isOpen ? "modal-open" : ""}`}>
      <div className="modal-box max-w-2xl">
        <div className="flex flex-col gap-2 rounded">
          <label htmlFor="name-input" className="font-medium">
            Name
          </label>
          <input
            id="name-input"
            name="name"
            type="text"
            className="bg-base-300 p-2 rounded"
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
                className="bg-base-300 p-2 rounded"
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
                className="bg-base-300 p-2 rounded"
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

          <label htmlFor="audio-input-mode" className="font-medium">
            Audio Sample
          </label>
          <Tip variant="info">Keep your audio file under 12 seconds.</Tip>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleAudioInputModeChange("upload")}
              className="btn btn-primary"
            >
              Upload Audio
            </button>
            <button
              type="button"
              onClick={() => handleAudioInputModeChange("record")}
              className="btn btn-primary"
            >
              Record Audio
            </button>
          </div>

          {audioFile && (
            <div className="text-sm text-success">
              ✓ Audio ready: {audioFile.name}
            </div>
          )}

          <label htmlFor="transcript-input" className="font-medium">
            Audio Transcript
          </label>
          <textarea
            id="transcript-input"
            name="audio_transcript"
            className="bg-base-300 p-2 rounded"
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
            className="btn btn-block"
          >
            {isSubmitting ? "Adding Voice..." : "Add Voice"}
          </button>
        </div>
        <div className="modal-action">
          <button onClick={handleClose} className="btn btn-ghost">
            Cancel
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={handleClose}></div>

      <dialog id="audio-modal" className="modal" ref={modalRef}>
        <div className="modal-box">
          <form method="dialog">
            <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">
              ✕
            </button>
          </form>
          <h3 className="font-bold text-lg mb-4">
            {audioInputMode === "upload" ? "Upload Audio File" : "Record Audio"}
          </h3>

          {audioInputMode === "upload" ? (
            <div className="flex flex-col gap-4">
              <Tip variant="info">Select an audio file under 12 seconds.</Tip>
              <input
                id="audio-file-input"
                name="audio_file"
                type="file"
                accept="audio/*"
                onChange={(e) => {
                  handleFileChange(e);
                  if (e.target.files && e.target.files[0]) {
                    handleModalFileSelect();
                  }
                }}
                className="file-input file-input-bordered w-full"
                required
              />
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              <AudioRecorder
                onRecordingComplete={handleModalRecordingComplete}
                maxDuration={12}
              />
            </div>
          )}
        </div>
        <form method="dialog" className="modal-backdrop">
          <button>close</button>
        </form>
      </dialog>
    </div>
  );
}
