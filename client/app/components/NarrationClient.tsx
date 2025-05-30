import React from "react";
import { use } from "react";

import NarrationAudio from "./NarrationAudio";
import NarrationButton from "./NarrationButton";

interface NarrationClientProps {
  narrationUrlPromise: Promise<string | null>;
}

export default function NarrationClient({
  narrationUrlPromise,
}: NarrationClientProps) {
  const narrationUrl = use(narrationUrlPromise);
  return (
    <>
      {narrationUrl ? (
        <NarrationAudio narrationUrl={narrationUrl} />
      ) : (
        <NarrationButton />
      )}
    </>
  );
}
