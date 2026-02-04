import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";

import * as schema from "./schema";

const connectionString = process.env.POSTGRES_URL;

if (!connectionString) {
  throw new Error("Missing POSTGRES_URL environment variable");
}

/**
 * Database client using postgres.js
 * Works with both local Docker containers and Neon (via standard connection string)
 */
const client = postgres(connectionString);

export const db = drizzle(client, {
  schema,
  casing: "snake_case",
});
