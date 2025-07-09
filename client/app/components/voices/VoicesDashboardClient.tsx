"use client";

import React from "react";
import { Suspense, useState } from "react";

import { Voice } from "../../actions/voices";

import VoiceAddModal from "./VoiceAddModal";
import VoiceList from "./VoiceList";

interface VoicesDashboardClientProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoicesDashboardClient({
  voicesPromise,
}: VoicesDashboardClientProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Suspense fallback={<div>Loading voices ...</div>}>
          <VoiceList voicesPromise={voicesPromise} />
        </Suspense>
        <button
          onClick={() => setIsModalOpen(true)}
          className="btn btn-block mt-4"
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
