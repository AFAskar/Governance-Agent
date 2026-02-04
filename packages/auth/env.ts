import { createEnv } from "@t3-oss/env-core";
import { z } from "zod/v4";

export function authEnv() {
  return createEnv({
    server: {
      WORKOS_API_KEY: z.string().min(1),
      WORKOS_CLIENT_ID: z.string().min(1),
      WORKOS_REDIRECT_URI: z.string().url(),
      WORKOS_COOKIE_PASSWORD: z.string().min(32),
      // Optional WorkOS configuration
      WORKOS_COOKIE_MAX_AGE: z.coerce.number().optional(),
      WORKOS_COOKIE_NAME: z.string().optional(),
      WORKOS_COOKIE_DOMAIN: z.string().optional(),
      WORKOS_COOKIE_SAMESITE: z.enum(["lax", "strict", "none"]).optional(),
      NODE_ENV: z.enum(["development", "production"]).optional(),
    },
    runtimeEnv: process.env,
    skipValidation:
      !!process.env.CI || process.env.npm_lifecycle_event === "lint",
  });
}
