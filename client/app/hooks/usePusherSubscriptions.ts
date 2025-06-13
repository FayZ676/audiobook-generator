import { useEffect } from "react";
import pusherClient from "@/app/lib/pusher";

interface ChannelConfig {
  channel: string;
  events: string[];
}

interface UsePusherSubscriptionsOptions {
  channels: ChannelConfig[];
  onUpdate?: (channel: string, event: string, data?: any) => void;
  dependencies?: any[];
}

export const usePusherSubscriptions = ({
  channels,
  onUpdate,
  dependencies = [],
}: UsePusherSubscriptionsOptions) => {
  useEffect(() => {
    const subscriptions = channels.map(({ channel, events }) => {
      const channelInstance = pusherClient.subscribe(channel);

      events.forEach((event) => {
        const handler = (data?: any) => {
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
  }, dependencies);
};
