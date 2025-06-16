import { useEffect } from "react";
import pusherClient from "@/app/lib/pusher";

interface ChannelConfig {
  channel: string;
  events: string[];
}

interface UsePusherSubscriptionsOptions {
  channels: ChannelConfig[];
  onUpdate?: (channel: string, event: string, data?: unknown) => void;
  dependencies?: React.DependencyList;
}

export const usePusherSubscriptions = ({
  channels,
  onUpdate,
  dependencies = [],
}: UsePusherSubscriptionsOptions) => {
  useEffect(() => {
    const subscriptions = channels.map(({ channel, events }) => {
      console.log(`Subscribing to channel: ${channel} with events:`, events);
      const channelInstance = pusherClient.subscribe(channel);

      events.forEach((event) => {
        const handler = (data?: unknown) => {
          console.log(`Pusher event received: ${event} on ${channel}`, data);
          onUpdate?.(channel, event, data);
        };
        channelInstance.bind(event, handler);
        console.log(`Bound event: ${event} on channel: ${channel}`);
      });

      return { channel, channelInstance, events };
    });

    return () => {
      subscriptions.forEach(({ channel, channelInstance, events }) => {
        console.log(`Unsubscribing from channel: ${channel}`);
        events.forEach((event) => {
          channelInstance.unbind(event);
        });
        pusherClient.unsubscribe(channel);
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);
};
