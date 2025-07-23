import { WebhookEvent } from "@clerk/nextjs/server";
import { Webhook } from "svix";
import { headers } from "next/headers";

import { sendSubscriptionEvent } from "@/app/actions/subscription";
import { ReadonlyHeaders } from "next/dist/server/web/spec-extension/adapters/headers";

const webhookSecret = process.env.CLERK_WEBHOOK_SECRET || ``;

async function validateRequest(request: Request) {
  const payloadString = await request.text();
  const headerPayload: ReadonlyHeaders = await headers();

  const svixHeaders = {
    "svix-id": headerPayload.get("svix-id")!,
    "svix-timestamp": headerPayload.get("svix-timestamp")!,
    "svix-signature": headerPayload.get("svix-signature")!,
  };
  const wh = new Webhook(webhookSecret);
  return wh.verify(payloadString, svixHeaders) as WebhookEvent;
}

export async function POST(request: Request) {
  const payload = await validateRequest(request);
  console.log(payload);
  // @ts-expect-error TypeScript does not know about the subscriptionItem.active event.
  if (payload.type === "subscriptionItem.active") {
    try {
      // @ts-expect-error TypeScript does not know about the payload structure.
      await sendSubscriptionEvent(payload.data.payer.user_id, payload.type);
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
