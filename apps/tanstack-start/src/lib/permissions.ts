/**
 * Submission permissions matching backend
 */
export const SUBMISSION_PERMISSIONS = {
  READ: "submissions:read",
  WRITE: "submissions:write",
  DELETE: "submissions:delete",
} as const;

export type SubmissionPermission =
  (typeof SUBMISSION_PERMISSIONS)[keyof typeof SUBMISSION_PERMISSIONS];

/**
 * Check if user has a specific permission
 */
export function hasPermission(
  userPermissions: string[] | undefined,
  requiredPermission: string,
): boolean {
  if (!userPermissions) return false;
  return userPermissions.includes(requiredPermission);
}

/**
 * Check if user has all required permissions
 */
export function hasAllPermissions(
  userPermissions: string[] | undefined,
  requiredPermissions: string[],
): boolean {
  if (!userPermissions) return false;
  return requiredPermissions.every((permission) =>
    userPermissions.includes(permission),
  );
}

/**
 * Check if user has any of the required permissions
 */
export function hasAnyPermission(
  userPermissions: string[] | undefined,
  requiredPermissions: string[],
): boolean {
  if (!userPermissions) return false;
  return requiredPermissions.some((permission) =>
    userPermissions.includes(permission),
  );
}
