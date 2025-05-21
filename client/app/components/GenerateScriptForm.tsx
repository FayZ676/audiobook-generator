import React from "react";

interface CreateScriptFormProps {
  action: (formData: FormData) => Promise<void>;
}

export default function CreateScriptForm({ action }: CreateScriptFormProps) {
  return (
    <form action={action} className="flex flex-col gap-4 max-w-sm">
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
