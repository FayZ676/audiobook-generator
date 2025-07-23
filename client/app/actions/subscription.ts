"use server";

export async function sendSubscriptionEvent(userId: string, eventType: string) {
  try {
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/subscription/${userId}/${eventType}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
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
