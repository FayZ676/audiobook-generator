import React from "react";

import VoicesDashboard from "../components/voices/VoicesDashboard";
import TabSection from "../components/ui/TabSection";

// Force dynamic rendering since this page uses authentication
export const dynamic = "force-dynamic";

export default function VoicesHome() {
  return (
    <div className="flex flex-col gap-4">
      <TabSection />
      <VoicesDashboard />
    </div>
  );
}
