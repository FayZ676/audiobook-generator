interface WebhookNotificationData {
  filename: string;
}

interface WebhookNotification {
  event: string;
  job_id: string;
  status: string;
  data: WebhookNotificationData;
}

export async function POST(request: Request) {
  try {
    const notification: WebhookNotification = await request.json();
    if (notification.event == "script") {
      // Revalidate script data.
    }
    if (notification.event == "narration") {
      // Revalidate narration data.
    }
  } catch (error) {
    console.error("Failed to parse JSON:", error);
    return new Response(JSON.stringify({ error: "Invalid JSON payload" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}
