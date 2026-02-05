import { WorkOS } from "@workos-inc/node";

const workosApiKey = process.env.WORKOS_API_KEY;

if (!workosApiKey) {
  throw new Error("WORKOS_API_KEY is not set");
}

export const workos = new WorkOS(workosApiKey);

/**
 * Submission permissions for RBAC
 */
export const SUBMISSION_PERMISSIONS = {
  READ: "submissions:read",
  WRITE: "submissions:write",
  DELETE: "submissions:delete",
} as const;

export type SubmissionPermission =
  (typeof SUBMISSION_PERMISSIONS)[keyof typeof SUBMISSION_PERMISSIONS];
