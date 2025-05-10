import { revalidatePath } from "next/cache";

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
    if (notification.event === "script" || notification.event === "narration") {
      // TODO: Can also update some DB state indicating the job status.
      revalidatePath("/");
    }
    return new Response("OK", {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Failed to parse JSON:", error);
    return new Response(JSON.stringify({ error: "Invalid JSON payload" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}
