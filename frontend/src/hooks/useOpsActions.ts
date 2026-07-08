/** Operations state — recommendations, action logging, alert management. */

import { useCallback, useEffect, useState } from "react";
import { getOpsRecommendations, listOpsActions, logOpsAction } from "../lib/api";
import { getDeviceId } from "../lib/deviceId";
import type { ActionType, OpsActionRecord, OpsRecommendation } from "../lib/types";

interface UseOpsActionsReturn {
  recommendations: OpsRecommendation[];
  actions: OpsActionRecord[];
  loading: boolean;
  error: string;
  takeAction: (actionType: ActionType, targetZone: string, notes: string) => Promise<void>;
  refreshRecommendations: () => Promise<void>;
}

export function useOpsActions(): UseOpsActionsReturn {
  const [recommendations, setRecommendations] = useState<OpsRecommendation[]>([]);
  const [actions, setActions] = useState<OpsActionRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const refreshRecommendations = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [recs, acts] = await Promise.all([getOpsRecommendations(), listOpsActions()]);
      setRecommendations(recs);
      setActions(acts);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshRecommendations();
  }, [refreshRecommendations]);

  const takeAction = useCallback(
    async (actionType: ActionType, targetZone: string, notes: string) => {
      try {
        const record = await logOpsAction({
          action_type: actionType,
          target_zone: targetZone,
          notes,
          operator_id: getDeviceId(),
        });
        setActions((prev) => [record, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to log action");
      }
    },
    [],
  );

  return { recommendations, actions, loading, error, takeAction, refreshRecommendations };
}
