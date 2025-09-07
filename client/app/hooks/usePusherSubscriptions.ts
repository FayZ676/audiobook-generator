import { useEffect } from "react";
import pusherClient from "@/app/lib/pusher";

interface ChannelConfig {
  channel: string;
  events: string[];
}

interface UsePusherSubscriptionsOptions {
  channels: ChannelConfig[];
  onUpdate: () => void;
}

export const usePusherSubscriptions = ({
  channels,
  onUpdate,
}: UsePusherSubscriptionsOptions) => {
  useEffect(() => {
    const handleStateChange = (states: {
      previous: string;
      current: string;
    }) => {
      if (states.previous === "connecting" && states.current === "connected") {
        onUpdate();
      }
    };

    pusherClient.connection.bind("state_change", handleStateChange);
    const subscriptions = channels.map(({ channel, events }) => {
      const channelInstance = pusherClient.subscribe(channel);

      events.forEach((event: string) => {
        const handler = () => {
          onUpdate();
        };
        channelInstance.bind(event, handler);
      });

      return { channel, channelInstance, events };
    });

    return () => {
      pusherClient.connection.unbind("state_change", handleStateChange);
      subscriptions.forEach(({ channel, channelInstance, events }) => {
        events.forEach((event: string) => {
          channelInstance.unbind(event);
        });
        pusherClient.unsubscribe(channel);
      });
    };
  }, [channels, onUpdate]);
};
