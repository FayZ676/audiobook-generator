import React from "react";

export default function UploadFileForm({
  action,
}: {
  action: (formData: FormData) => Promise<void>;
}) {
  return (
    <form action={action} className="flex flex-col gap-4 max-w-sm">
      <label htmlFor="file-input">Upload Text File</label>
      <input
        id="file-input"
        name="file"
        type="file"
        accept=".txt"
        className="border"
      />
      <button type="submit">Upload</button>
    </form>
  );
}
