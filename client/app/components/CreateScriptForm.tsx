import React from "react";

export default function CreateScriptForm({
  action,
}: {
  action: (formData: FormData) => Promise<void>;
}) {
  return (
    <form action={action} className="flex flex-col gap-4 max-w-sm">
      <h2>Generate Script</h2>
      <label htmlFor="filename-input">File Name</label>
      <input
        id="filename-input"
        name="filename"
        type="text"
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
