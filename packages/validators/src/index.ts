import { z } from "zod/v4";

export const unused = z
  .string()
  .describe(`non-drizzle zod validation should be done in this package`);

export * from "./ndi-domains";
