"use client";

import { useUser } from "@clerk/nextjs";

export const ChannelEvents = ["processing", "complete", "failed"];

export const getUserSpecificChannels = (userId: string) => ({
  SPEECH_CHANNEL: {
    channel: `${userId}-speech`,
    events: ChannelEvents,
  },
  SCRIPT_CHANNEL: {
    channel: `${userId}-script`,
    events: ChannelEvents,
  },
  VOICES_CHANNEL: {
    channel: `${userId}-voices`,
    events: ChannelEvents,
  },
});

export const useUserChannels = () => {
  const { isLoaded, user } = useUser();

  if (!isLoaded) {
    return null;
  }

  const id = user?.id;

  if (!id) {
    throw new Error("User must be authenticated to access pusher channels");
  }

  return getUserSpecificChannels(id);
};
