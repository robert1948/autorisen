/**
 * Role constants and permission definitions for CapeControl.
 *
 * The backend enforces the same constraints at the API level.
 * These client-side definitions are a convenience layer for
 * conditional rendering — never a security boundary.
 */

import type { UserRole } from "../types/user";

/** Ordered by privilege level (lowest → highest) */
export const ROLES: readonly UserRole[] = ["user", "developer", "admin"] as const;

/**
 * Permission strings follow the pattern `resource:action`.
 * Admin role uses the wildcard `*` to grant all permissions.
 */
export const ROLE_PERMISSIONS: Record<UserRole, readonly string[]> = {
  user: [
    "profile:read",
    "profile:edit",
    "projects:read",
    "projects:create",
    "account:billing",
    "account:delete",
  ],
  developer: [
    "profile:read",
    "profile:edit",
    "projects:read",
    "projects:create",
    "projects:audit",
    "apikeys:manage",
    "workflows:manage",
    "account:billing",
    "account:delete",
  ],
  admin: ["*"],
} as const;

/** Human-friendly role labels */
export const ROLE_LABELS: Record<UserRole, string> = {
  user: "User",
  developer: "Developer",
  admin: "Admin",
};

/** Session timeout per role (minutes of inactivity) */
export const SESSION_TIMEOUT: Record<UserRole, number> = {
  user: 30,
  developer: 30,
  admin: 10,
};
