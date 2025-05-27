import React from "react";

import { NarrationUrl } from "../actions/narrate";

interface NarrationViewProps {
  narrationUrl: NarrationUrl;
}

export default function NarrationView({ narrationUrl }: NarrationViewProps) {
  return (
    <audio controls preload="none">
      <source src={narrationUrl} />
      Your browser does not support the audio element.
    </audio>
  );
}
