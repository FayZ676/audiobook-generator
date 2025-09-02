import { useEffect, useRef, useCallback } from "react";
import pusherClient from "@/app/lib/pusher";

interface ChannelConfig {
  channel: string;
  events: string[];
}

interface UsePusherSubscriptionsOptions {
  channels: (ChannelConfig | null)[] | null;
  onUpdate?: (channel: string, event: string, data?: unknown) => void;
  onReconnection?: () => void;
  pollingInterval?: number;
  shouldPoll?: () => boolean;
}

export const usePusherSubscriptions = ({
  channels,
  onUpdate,
  onReconnection,
  pollingInterval = 5000,
  shouldPoll,
}: UsePusherSubscriptionsOptions) => {
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const hasInitializedRef = useRef(false);

  const startPolling = useCallback(() => {
    if (!shouldPoll || pollingIntervalRef.current) return;

    pollingIntervalRef.current = setInterval(() => {
      if (shouldPoll?.()) {
        onReconnection?.();
      }
    }, pollingInterval);
  }, [shouldPoll, onReconnection, pollingInterval]);
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    const validChannels =
      channels?.filter(
        (channel): channel is ChannelConfig => channel !== null
      ) || [];

    if (validChannels.length === 0) {
      stopPolling();
      return;
    }

    // Handle initial mount - sync state once
    if (!hasInitializedRef.current && onReconnection) {
      hasInitializedRef.current = true;
      onReconnection();
    }

    const subscriptions = validChannels.map(({ channel, events }) => {
      const channelInstance = pusherClient.subscribe(channel);

      events.forEach((event: string) => {
        channelInstance.bind(event, (data?: unknown) => {
          onUpdate?.(channel, event, data);
        });
      });

      return { channel, channelInstance, events };
    });

    if (onReconnection) {
      pusherClient.connection.bind("connected", onReconnection);
    }
    pusherClient.connection.bind("disconnected", startPolling);
    pusherClient.connection.bind(
      "state_change",
      (states: { current: string; previous: string }) => {
        if (
          states.previous === "disconnected" &&
          states.current === "connected"
        ) {
          stopPolling();
          onReconnection?.();
        }
      }
    );

    // Start polling if we should be polling
    startPolling();

    return () => {
      if (onReconnection) {
        pusherClient.connection.unbind("connected", onReconnection);
      }
      pusherClient.connection.unbind("disconnected", startPolling);
      pusherClient.connection.unbind("state_change");

      stopPolling();

      subscriptions.forEach(({ channel, channelInstance, events }) => {
        events.forEach((event: string) => {
          channelInstance.unbind(event);
        });
        pusherClient.unsubscribe(channel);
      });
    };
  }, [
    channels,
    onUpdate,
    onReconnection,
    startPolling,
    stopPolling,
    shouldPoll,
  ]);
};
