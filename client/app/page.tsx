import { createScript } from "@/app/actions/script";

export default function Home() {
  return (
    <div>
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
    </div>
  );
}
