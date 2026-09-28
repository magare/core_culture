import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { env } from "@/lib/env";
import * as schema from "./schema";

const globalDb = globalThis as unknown as { coreCulturePool?: Pool };
export const pool = globalDb.coreCulturePool ?? new Pool({
  connectionString: env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 20_000,
  connectionTimeoutMillis: 5_000,
  statement_timeout: 10_000,
});
if (process.env.NODE_ENV !== "production") globalDb.coreCulturePool = pool;
if (pool.listenerCount("error") === 0) {
  pool.on("error", () => console.error("An idle database connection failed. Check PostgreSQL availability."));
}
export const db = drizzle(pool, { schema });
