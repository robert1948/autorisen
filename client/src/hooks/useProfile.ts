/**
 * useProfile — enhanced profile hook with stale-while-revalidate caching.
 *
 * Wraps the existing `useMe()` data and normalises it into the
 * UserProfile shape expected by the role-aware dashboard.
 *
 * Refresh triggers (per spec §1.3):
 *   - Profile edit saved
 *   - Role change detected
 *   - Manual refresh action
 *   - Re-authentication
 *
 * TTL: profile cache is considered stale after 5 minutes.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { getMe, type MeResponse } from "../lib/authApi";
import type { UserProfile, UserRole, UserStatus } from "../types/user";

/** Cache TTL in milliseconds (5 minutes) */
const PROFILE_CACHE_TTL = 5 * 60 * 1000;

interface ProfileState {
  user: UserProfile | null;
  isLoading: boolean;
  error: { status?: number; message: string } | null;
}

/**
 * Map the existing backend MeResponse to the expanded UserProfile shape.
 * Fields not yet available from the backend are given safe defaults
 * so the dashboard can render immediately.
 */
function mapMeToProfile(me: MeResponse): UserProfile {
  const profile = me.profile;
  const role = (me.role ?? "user") as UserRole;

  return {
    userId: profile.id,
    email: profile.email,
    emailVerified: profile.email_verified ?? false,
    role,
    name: [profile.first_name, profile.last_name].filter(Boolean).join(" ") || profile.display_name,
    displayName: profile.display_name || profile.email.split("@")[0],
    avatarUrl: null,
    createdAt: profile.created_at,
    lastLogin: profile.last_login ?? profile.created_at,
    status: (profile.status || "active") as UserStatus,
    preferences: {
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      locale: navigator.language ?? "en",
      notificationsEnabled: true,
    },
    account: {
      balance: 0,
      currency: "USD",
      subscriptionTier: "free",
    },
    developerProfile: role === "developer" || role === "admin"
      ? {
          developerId: profile.id,
          apiKeyStatus: "active",
          apiKeysCount: 0,
          approvedWorkflowsCount: 0,
          webhookEndpoints: [],
          usageQuota: {
            apiCallsUsed: 0,
            apiCallsLimit: 10_000,
            resetDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          },
        }
      : null,
  };
}

export function useProfile() {
  const [state, setState] = useState<ProfileState>({
    user: null,
    isLoading: true,
    error: null,
  });

  const lastFetchedAt = useRef<number>(0);
  const isMounted = useRef(true);

  const fetchProfile = useCallback(async (background = false) => {
    if (!background) {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
    }

    try {
      const me = await getMe();
      const user = mapMeToProfile(me);
      lastFetchedAt.current = Date.now();

      if (isMounted.current) {
        setState({ user, isLoading: false, error: null });
      }
    } catch (err) {
      const status = (err as { status?: number }).status;
      const message = (err as Error).message || "Failed to load profile";

      if (isMounted.current) {
        setState((prev) => ({
          user: background ? prev.user : null, // keep stale data on background refresh
          isLoading: false,
          error: { status, message },
        }));
      }
    }
  }, []);

  /** Force a foreground refetch */
  const refetch = useCallback(() => fetchProfile(false), [fetchProfile]);

  // Initial load
  useEffect(() => {
    isMounted.current = true;
    fetchProfile(false);
    return () => {
      isMounted.current = false;
    };
  }, [fetchProfile]);

  // Stale-while-revalidate: background refresh after TTL
  useEffect(() => {
    const interval = setInterval(() => {
      if (Date.now() - lastFetchedAt.current > PROFILE_CACHE_TTL) {
        fetchProfile(true);
      }
    }, 60_000); // check every minute

    return () => clearInterval(interval);
  }, [fetchProfile]);

  return { ...state, refetch };
}
