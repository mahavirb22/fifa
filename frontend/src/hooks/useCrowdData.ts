/** Crowd density state — auto-refreshing every 30s. */

import { useCallback, useEffect, useState } from "react";
import { getCrowdDensity } from "../lib/api";
import type { CrowdAnalysis } from "../lib/types";

interface UseCrowdDataReturn {
  crowdData: CrowdAnalysis | null;
  loading: boolean;
  error: string;
  refresh: () => Promise<void>;
}

export function useCrowdData(): UseCrowdDataReturn {
  const [crowdData, setCrowdData] = useState<CrowdAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getCrowdDensity();
      setCrowdData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load crowd data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const interval = setInterval(() => void refresh(), 30_000);
    return () => clearInterval(interval);
  }, [refresh]);

  return { crowdData, loading, error, refresh };
}
