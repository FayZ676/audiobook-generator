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
  enablePolling?: boolean;
  pollingInterval?: number;
  shouldPoll?: () => boolean;
}

export const usePusherSubscriptions = ({
  channels,
  onUpdate,
  onReconnection,
  enablePolling = false,
  pollingInterval = 5000,
  shouldPoll,
}: UsePusherSubscriptionsOptions) => {
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const hasInitializedRef = useRef(false);

  const startPolling = useCallback(() => {
    if (!enablePolling || !shouldPoll || pollingIntervalRef.current) return;
    
    pollingIntervalRef.current = setInterval(() => {
      if (shouldPoll?.()) {
        onReconnection?.();
      }
    }, pollingInterval);
  }, [enablePolling, shouldPoll, onReconnection, pollingInterval]);

  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!channels || channels.length === 0) {
      stopPolling();
      return;
    }

    const validChannels = channels.filter(
      (channel): channel is ChannelConfig => channel !== null
    );

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
        const handler = (data?: unknown) => {
          onUpdate?.(channel, event, data);
        };
        channelInstance.bind(event, handler);
      });

      return { channel, channelInstance, events };
    });

    // Handle Pusher connection state changes
    const handleConnected = () => {
      // When reconnected, sync state to catch any missed events
      onReconnection?.();
    };

    const handleDisconnected = () => {
      // Start polling when disconnected to ensure we don't miss updates
      if (enablePolling) {
        startPolling();
      }
    };

    const handleReconnected = () => {
      // Stop polling when reconnected and sync state
      stopPolling();
      onReconnection?.();
    };

    // Bind to connection state events
    pusherClient.connection.bind('connected', handleConnected);
    pusherClient.connection.bind('disconnected', handleDisconnected);
    pusherClient.connection.bind('state_change', (states: { current: string; previous: string }) => {
      if (states.previous === 'disconnected' && states.current === 'connected') {
        handleReconnected();
      }
    });

    // Start polling if we should be polling
    if (enablePolling && shouldPoll?.()) {
      startPolling();
    }

    return () => {
      // Unbind connection state events
      pusherClient.connection.unbind('connected', handleConnected);
      pusherClient.connection.unbind('disconnected', handleDisconnected);
      pusherClient.connection.unbind('state_change');
      
      stopPolling();

      subscriptions.forEach(({ channel, channelInstance, events }) => {
        events.forEach((event: string) => {
          channelInstance.unbind(event);
        });
        pusherClient.unsubscribe(channel);
      });
    };
  }, [channels, onUpdate, onReconnection, startPolling, stopPolling, enablePolling, shouldPoll]);
};
