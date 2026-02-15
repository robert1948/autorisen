/**
 * Permission checking utilities for role-aware rendering.
 *
 * Usage:
 *   import { hasPermission } from '@/utils/permissions';
 *   {hasPermission(user, 'workflows:manage') && <WorkflowManagement />}
 *
 * The backend MUST enforce the same restrictions at the API level.
 * These helpers are a UI convenience layer, not a security boundary.
 */

import { ROLE_PERMISSIONS } from "../constants/roles";
import type { UserRole } from "../types/user";

interface RoleHolder {
  role: UserRole | string;
}

/**
 * Check whether a user has a specific permission.
 * Admin role (`*` wildcard) is automatically granted everything.
 */
export function hasPermission(user: RoleHolder, permission: string): boolean {
  const role = (user.role ?? "user") as UserRole;
  const permissions = ROLE_PERMISSIONS[role] ?? ROLE_PERMISSIONS.user;
  return permissions.includes("*") || permissions.includes(permission);
}

/**
 * Check whether a user has ALL of the listed permissions.
 */
export function hasAllPermissions(user: RoleHolder, perms: string[]): boolean {
  return perms.every((p) => hasPermission(user, p));
}

/**
 * Check whether a user has ANY of the listed permissions.
 */
export function hasAnyPermission(user: RoleHolder, perms: string[]): boolean {
  return perms.some((p) => hasPermission(user, p));
}

/**
 * Check whether the user's role meets a minimum privilege level.
 */
export function isAtLeast(user: RoleHolder, minRole: UserRole): boolean {
  const hierarchy: Record<string, number> = { user: 0, developer: 1, admin: 2 };
  const userLevel = hierarchy[user.role] ?? 0;
  const minLevel = hierarchy[minRole] ?? 0;
  return userLevel >= minLevel;
}
