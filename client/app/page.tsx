export default function Home() {
  async function createScript(formData: FormData) {
    "use server";

    const file = formData.get("file") as File;
    const narrator = formData.get("narrator") as string;

    const serverFormData = new FormData();
    serverFormData.append("file", file);

    fetch(
      `https://audiobook-generator-lux1.onrender.com/script?narrator=${encodeURIComponent(
        narrator
      )}`,
      {
        method: "POST",
        body: serverFormData,
        headers: {
          "Content-Type": "application/json",
        },
      }
    )
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

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
