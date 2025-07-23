import { WebhookEvent } from "@clerk/nextjs/server";

export async function POST(request: Request) {
  const payload: WebhookEvent = await request.json();
  console.log(payload);
  return Response.json({ message: "Webhook received" });
}

export async function GET() {
  return Response.json({ message: "Hello World!" });
}
