import { createScript, getScripts } from "@/app/actions/script";

export default async function Home() {
  const scripts = await getScripts();
  // Get narrations as well.

  return (
    <div className="max-w-md">
      <form action={createScript} className="flex flex-col gap-4 max-w-sm">
        <label htmlFor="file-input">Text File</label>
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
