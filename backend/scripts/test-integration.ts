import { spawn, type ChildProcess } from "node:child_process";
import { randomBytes } from "node:crypto";
import { once } from "node:events";
import { createServer } from "node:net";
import { config } from "dotenv";
import { Pool } from "pg";
import { drizzle } from "drizzle-orm/node-postgres";
import { migrate } from "drizzle-orm/node-postgres/migrator";

config({ path: ".env.local", quiet: true });
const source = new URL(process.env.DATABASE_URL ?? "");
if (!["localhost", "127.0.0.1", "[::1]"].includes(source.hostname)) throw new Error("Integration tests only create databases on local PostgreSQL.");
const databaseName = `core_culture_test_${randomBytes(6).toString("hex")}`;
const adminUrl = new URL(source); adminUrl.pathname = "/postgres";
const admin = new Pool({ connectionString: adminUrl.toString() });
const databaseUrl = new URL(source); databaseUrl.pathname = `/${databaseName}`;
let created = false, server: ChildProcess | undefined, logs = "";
const socket = createServer(); socket.listen(0, "127.0.0.1"); await once(socket, "listening");
const address = socket.address();
if (!address || typeof address === "string") throw new Error("Unable to reserve a test port.");
const port = address.port; await new Promise<void>((resolve) => socket.close(() => resolve()));
const env = { ...process.env, DATABASE_URL: databaseUrl.toString(), BETTER_AUTH_URL: `http://127.0.0.1:${port}`,
  BETTER_AUTH_SECRET: randomBytes(48).toString("base64url"), MAIL_MODE: "outbox", MAIL_OUTBOX_DIR: `.local/${databaseName}/mail`,
  NEXT_DIST_DIR: ".next-test", NODE_ENV: "development" as const, NEXT_TELEMETRY_DISABLED: "1", INTEGRATION_TEST: "1" };

try {
  // Generated identifier is validated again before interpolation into DDL.
  if (!/^core_culture_test_[a-f0-9]{12}$/.test(databaseName)) throw new Error("Invalid test database name.");
  await admin.query(`CREATE DATABASE "${databaseName}"`); created = true;
  const pool = new Pool({ connectionString: databaseUrl.toString() });
  try { await migrate(drizzle(pool), { migrationsFolder: "./drizzle" }); }
  finally { await pool.end(); }
  console.log("Migrated a fresh, isolated PostgreSQL test database.");
  server = spawn(process.execPath, ["node_modules/next/dist/bin/next", "dev", "--hostname", "127.0.0.1", "--port", String(port)], { env, stdio: ["ignore", "pipe", "pipe"] });
  const collect = (data: Buffer) => { logs = (logs + data.toString()).slice(-20_000); };
  server.stdout?.on("data", collect); server.stderr?.on("data", collect);
  let ready = false;
  for (let attempt = 0; attempt < 120; attempt++) {
    if (server.exitCode !== null) throw new Error("Test server exited unexpectedly.");
    try { if ((await fetch(`${env.BETTER_AUTH_URL}/api/health`, { signal: AbortSignal.timeout(2000) })).ok) { ready = true; break; } } catch { /* Server is compiling. */ }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  if (!ready) throw new Error("Test server did not become ready.");
  console.log("Running HTTP integration tests against the real Next.js server.");
  const tests = spawn(process.execPath, ["--import", "tsx", "--test", "--test-concurrency=1", "tests/api.integration.ts"], { env, stdio: "inherit" });
  const [code] = await once(tests, "exit");
  if (code !== 0) throw new Error("Integration tests failed.");
} catch (error) {
  console.error(logs);
  console.error(error instanceof Error ? error.message : "Integration run failed.");
  process.exitCode = 1;
} finally {
  if (server && server.exitCode === null) {
    const exit = once(server, "exit"); server.kill("SIGTERM");
    await exit;
  }
  if (created) {
    // Only the exact scratch database created by this invocation is dropped.
    await admin.query(`DROP DATABASE "${databaseName}" WITH (FORCE)`);
    console.log("Removed this run's scratch database; development data was untouched.");
  }
  await admin.end();
}
