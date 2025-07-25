"use server";

export async function sendSubscriptionEvent(userId: string) {
  try {
    const response = await fetch(
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

    if (!response.ok) {
      throw new Error(
        `Failed to send subscription event: ${response.statusText}`
      );
    }

    return { success: true };
  } catch (error) {
    console.error("Error sending subscription event:", error);
    throw error;
  }
}
