import { WebhookEvent } from "@clerk/nextjs/server";

import { sendSubscriptionEvent } from "@/app/actions/subscription";

export async function POST(request: Request) {
  const payload: WebhookEvent = await request.json();
  console.log(payload);
  // @ts-expect-error TypeScript does not know about the subscriptionItem.active event.
  if (payload.type === "subscriptionItem.active") {
    try {
      await sendSubscriptionEvent("subscription_active");
    } catch (error) {
      console.error("Error sending subscription created event:", error);
      return Response.json(
        { error: "Failed to process subscription event" },
        { status: 500 }
      );
    }
  }
  return Response.json({ message: "Webhook received" });
}
