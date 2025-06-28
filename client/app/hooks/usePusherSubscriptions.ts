import { useEffect } from "react";
import pusherClient from "@/app/lib/pusher";

interface ChannelConfig {
  channel: string;
  events: string[];
}

interface UsePusherSubscriptionsOptions {
  channels: ChannelConfig[];
  onUpdate?: (channel: string, event: string, data?: unknown) => void;
}

export const usePusherSubscriptions = ({
  channels,
  onUpdate,
}: UsePusherSubscriptionsOptions) => {
  useEffect(() => {
    const subscriptions = channels.map(({ channel, events }) => {
      const channelInstance = pusherClient.subscribe(channel);

      events.forEach((event) => {
        const handler = (data?: unknown) => {
          onUpdate?.(channel, event, data);
        };
        channelInstance.bind(event, handler);
      });

      return { channel, channelInstance, events };
    });

    return () => {
      subscriptions.forEach(({ channel, channelInstance, events }) => {
        events.forEach((event) => {
          channelInstance.unbind(event);
        });
        pusherClient.unsubscribe(channel);
      });
    };
  }, [channels, onUpdate]);
};
