import React from "react";

import { createNarration } from "../actions/narrate";

export default function NarrationButton() {
  return (
    <form action={createNarration}>
      <button className="ml-auto border py-2 px-4">Narrate</button>
    </form>
  );
}
