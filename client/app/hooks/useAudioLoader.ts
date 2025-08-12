import { useState, useCallback } from "react";

interface UseAudioLoaderOptions {
  onError?: (error: Error) => void;
}

export function useAudioLoader(options: UseAudioLoaderOptions = {}) {
  const [urls, setUrls] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});

  const loadAudio = useCallback(
    async (key: string, loader: () => Promise<string>) => {
      if (urls[key] || loading[key]) return;

      setLoading((prev) => ({ ...prev, [key]: true }));
      try {
        const url = await loader();
        setUrls((prev) => ({ ...prev, [key]: url }));
      } catch (error) {
        const err = error instanceof Error ? error : new Error("Failed to load audio");
        options.onError?.(err);
        console.error("Failed to load audio:", err);
      } finally {
        setLoading((prev) => ({ ...prev, [key]: false }));
      }
    },
    [urls, loading, options]
  );

  const getUrl = useCallback((key: string) => urls[key], [urls]);
  const isLoading = useCallback((key: string) => !!loading[key], [loading]);

  return {
    loadAudio,
    getUrl,
    isLoading,
  };
}
