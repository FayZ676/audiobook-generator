import React from "react";

import { createScript } from "../actions/script";

export default function CreateScriptForm() {
  return (
    <form action={createScript} className="flex flex-col gap-4 max-w-sm">
      <h2>Generate Script</h2>
      <label htmlFor="filename-input">Text File</label>
      <input
        id="file-input"
        name="file"
        type="file"
        accept=".txt"
        className="border"
      />
      <label htmlFor="narrator-input">Narrator Voice Name</label>
      <input
        id="narrator-input"
        name="narrator"
        type="text"
        className="border"
      />
      <button type="submit">Submit</button>
    </form>
  );
}
