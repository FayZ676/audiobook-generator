"use server";

export async function createScript(formData: FormData) {
  const file = formData.get("file") as File;
  const narrator = formData.get("narrator") as string;

  const serverFormData = new FormData();
  serverFormData.append("file", file);

  fetch(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script?narrator=${encodeURIComponent(
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
