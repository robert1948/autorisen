import { useCallback, useEffect, useState } from "react";

import { getMe, type MeResponse } from "../lib/authApi";

type MeState = {
  loading: boolean;
  error: string | null;
  status?: number;
  data: MeResponse | null;
};

export function useMe() {
  const [state, setState] = useState<MeState>({
    loading: true,
    error: null,
    status: undefined,
    data: null,
  });

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null, status: undefined }));
    try {
      const data = await getMe();
      setState({ loading: false, error: null, status: undefined, data });
    } catch (err) {
      const status = (err as { status?: number }).status;
      const message = (err as Error).message || "Failed to load identity";
      setState({ loading: false, error: message, status, data: null });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, reload: load };
}
