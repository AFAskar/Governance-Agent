/**
 * WorkOS AuthKit session types for TanStack Start
 *
 * This module re-exports the authentication types from the WorkOS AuthKit SDK
 * for use throughout the application.
 */
export type {
  UserInfo,
  NoUserInfo,
} from "@workos/authkit-tanstack-react-start";

// Re-export server functions for convenience
export {
  getAuth,
  signOut,
  getSignInUrl,
  getSignUpUrl,
  getAuthorizationUrl,
  switchToOrganization,
} from "@workos/authkit-tanstack-react-start";
