"use client";

import React from "react";
import { useState, use } from "react";

import { Plus } from "lucide-react";

import type { Voice } from "../../actions/voices";

import VoiceAddModal from "./VoiceAddModal";
import VoiceCard from "./VoiceCard";

interface VoicesDashboardClientProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoicesDashboardClient({
  voicesPromise,
}: VoicesDashboardClientProps) {
  const voices = use(voicesPromise);
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2 w-full">
      <h4>Voices</h4>
      {voices.length > 0 && (
        <div className="flex flex-col max-h-80 overflow-y-scroll">
          {voices.map((voice) => (
            <VoiceCard key={voice.name} voice={voice} />
          ))}
        </div>
      )}
      <button
        onClick={() => setIsModalOpen(true)}
        className="btn btn-block mt-4 text-gray-500"
      >
        <Plus className="h-4 w-4" />
        Add Voice
      </button>
      <VoiceAddModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
