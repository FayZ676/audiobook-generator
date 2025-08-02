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
    <div className="flex flex-col gap-2 w-full">
      <Suspense
        fallback={
          <div className="flex items-center gap-2">
            Loading voices{" "}
            <span className="loading loading-dots loading-xs"></span>
          </div>
        }
      >
        <VoiceList voicesPromise={voicesPromise} />
      </Suspense>
      <button
        onClick={() => setIsModalOpen(true)}
        className="btn btn-block mt-4"
      >
        Add New Voice
      </button>
      <VoiceAddModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
