"use client";

import React from "react";
import { Suspense, useState } from "react";

import { getVoices } from "../../actions/voices";

import VoiceAddModal from "./VoiceAddModal";
import VoiceList from "./VoiceList";

export default function VoicesDashboard() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const voicesPromise = getVoices();

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-md font-semibold mb-4">Voice clones</h2>
        <Suspense fallback={<div>Loading voices ...</div>}>
          <VoiceList voicesPromise={voicesPromise} />
        </Suspense>
        <button
          onClick={() => setIsModalOpen(true)}
          className="btn btn-primary btn-block mt-4"
        >
          Add New Voice
        </button>
      </div>
      <VoiceAddModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
