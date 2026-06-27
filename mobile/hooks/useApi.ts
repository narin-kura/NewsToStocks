import { useState, useCallback } from "react";
import { API_BASE } from "../constants/api";

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const call = useCallback(
    async <T>(endpoint: string, options?: RequestInit): Promise<T | null> => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
          headers: { "Content-Type": "application/json" },
          ...options,
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body.error ?? body.detail ?? `HTTP ${res.status}`);
        }
        return (await res.json()) as T;
      } catch (e: any) {
        setError(e.message ?? "Network error");
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return { call, loading, error };
}
