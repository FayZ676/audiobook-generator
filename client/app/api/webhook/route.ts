export async function POST(request: Request) {
  try {
    const body = await request.json();
    // TODO: Extract and display the script or speech result.
  } catch (error) {
    console.error("Failed to parse JSON:", error);
    return new Response(JSON.stringify({ error: "Invalid JSON payload" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}
