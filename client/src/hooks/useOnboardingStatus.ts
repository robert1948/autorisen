import { useCallback, useEffect, useState } from "react";

import { getOnboardingStatus, type OnboardingStatus } from "../api/onboarding";

type OnboardingState = {
  loading: boolean;
  error: string | null;
  status?: number;
  data: OnboardingStatus | null;
};

export function useOnboardingStatus() {
  const [state, setState] = useState<OnboardingState>({
    loading: true,
    error: null,
    status: undefined,
    data: null,
  });

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null, status: undefined }));
    try {
      const data = await getOnboardingStatus();
      setState({ loading: false, error: null, status: undefined, data });
    } catch (err) {
      const status = (err as { status?: number }).status;
      const message = (err as Error).message || "Failed to load onboarding status";
      setState({ loading: false, error: message, status, data: null });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, reload: load };
}
