import { useEffect } from "react";
import pusherClient from "@/app/lib/pusher";

interface ChannelConfig {
  channel: string;
  events: string[];
}

interface UsePusherSubscriptionsOptions {
  channels: (ChannelConfig | null)[] | null;
  onUpdate?: (channel: string, event: string, data?: unknown) => void;
}

export const usePusherSubscriptions = ({
  channels,
  onUpdate,
}: UsePusherSubscriptionsOptions) => {
  useEffect(() => {
    // TODO: If pusher.client is in connected state, we should revalidate the data of whatever component uses this hook.

    if (!channels || channels.length === 0) {
      return;
    }

    const validChannels = channels.filter(
      (channel): channel is ChannelConfig => channel !== null
    );

    if (validChannels.length === 0) {
      return;
    }

    const subscriptions = validChannels.map(({ channel, events }) => {
      const channelInstance = pusherClient.subscribe(channel);

      events.forEach((event: string) => {
        const handler = (data?: unknown) => {
          onUpdate?.(channel, event, data);
        };
        channelInstance.bind(event, handler);
      });

      return { channel, channelInstance, events };
    });

    return () => {
      subscriptions.forEach(({ channel, channelInstance, events }) => {
        events.forEach((event: string) => {
          channelInstance.unbind(event);
        });
        pusherClient.unsubscribe(channel);
      });
    };
  }, [channels, onUpdate]);
};
