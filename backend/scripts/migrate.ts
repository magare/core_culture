import { config } from "dotenv";
import { migrate } from "drizzle-orm/node-postgres/migrator";

config({ path: ".env.local", quiet: true });
const { db, pool } = await import("../src/db/index");
try {
  await migrate(db, { migrationsFolder: "./drizzle" });
  console.log("Database migrations applied.");
} finally { await pool.end(); }
