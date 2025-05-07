export async function POST(request: Request) {
  try {
    const body = await request.json();
    // TODO: Check the type and status of the event. i.e. fetch script/speech if success.
  } catch (error) {
    console.error("Failed to parse JSON:", error);
    return new Response(JSON.stringify({ error: "Invalid JSON payload" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}
