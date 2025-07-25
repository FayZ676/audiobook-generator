"use server";

import { apiCallVoid } from "../lib/api";

export async function sendSubscriptionEvent(userId: string) {
  try {
    await apiCallVoid(
      `${process.env.AUDIOBOOK_SERVICE_URL}/events`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          event: "subscription_reset",
          status: "complete",
          message: null,
          data: {
            request_word_count: 0,
          },
        }),
      }
    );

    return { success: true };
  } catch (error) {
    console.error("Error sending subscription event:", error);
    throw error;
  }
}
