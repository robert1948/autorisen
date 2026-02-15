/**
 * User & role types for the CapeControl dashboard.
 * Aligned with backend UserRole enum and /api/auth/me response schema.
 */

export type UserRole = "user" | "developer" | "admin";

export type UserStatus =
  | "active"
  | "suspended"
  | "pending_verification"
  | "deactivated";

export type SubscriptionTier = "free" | "pro" | "enterprise";
export type ApiKeyStatus = "active" | "revoked" | "expired";

export interface UserPreferences {
  timezone: string;
  locale: string;
  notificationsEnabled: boolean;
}

export interface UserAccount {
  balance: number;
  currency: string;
  subscriptionTier: SubscriptionTier;
}

export interface UsageQuota {
  apiCallsUsed: number;
  apiCallsLimit: number;
  resetDate: string; // ISO-8601
}

export interface DeveloperProfile {
  developerId: string;
  apiKeyStatus: ApiKeyStatus;
  apiKeysCount: number;
  approvedWorkflowsCount: number;
  webhookEndpoints: string[];
  usageQuota: UsageQuota;
}

/**
 * Unified user profile returned from /api/auth/me.
 * Extends the existing MeResponse shape with the expanded fields
 * described in the Dashboard Content Requirements v2.0.
 */
export interface UserProfile {
  userId: string;
  email: string;
  emailVerified: boolean;
  role: UserRole;
  name: string;
  displayName: string;
  avatarUrl: string | null;
  createdAt: string; // ISO-8601
  lastLogin: string; // ISO-8601
  status: UserStatus;
  preferences: UserPreferences;
  account: UserAccount;
  developerProfile: DeveloperProfile | null;
}

/**
 * Lightweight shape used when the full profile hasn't loaded yet
 * but we know the user's role from the auth context.
 */
export interface MinimalUser {
  role: UserRole;
  displayName: string;
  email: string;
}
