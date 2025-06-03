import React from "react";

import { getVoices } from "../actions/voices";
import VoicesSection from "../components/VoicesSection";
import TabSection from "../components/TabSection";

export default function VoicesHome() {
  const voicesPromise = getVoices();

  return (
    <div>
      <TabSection />
      <div className="flex flex-col gap-4">
        <VoicesSection voicesPromise={voicesPromise} />
      </div>
    </div>
  );
}
