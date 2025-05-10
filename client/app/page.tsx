import { createScript, getScripts } from "@/app/actions/script";
import { uploadTextFile } from "@/app/actions/file";

export default async function Home() {
  const scripts = await getScripts();
  // Get narrations as well.

  return (
    <div className="max-w-md">
      <form action={uploadTextFile}>
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

      <form action={createScript} className="flex flex-col gap-4 max-w-sm">
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

      <div className="flex flex-col gap-4">
        {scripts.map((script) => (
          <div key={script.filename} className="border p-4">
            <p>{script.filename}</p>
          </div>
        ))}
        {scripts.length === 0 && <p>No scripts available.</p>}
      </div>
    </div>
  );
}
