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
