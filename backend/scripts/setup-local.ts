import { randomBytes } from "node:crypto";
import { access, writeFile } from "node:fs/promises";
import { userInfo } from "node:os";
import { Pool } from "pg";

try {
  await access(".env.local");
  console.log(".env.local already exists; nothing changed. Run npm run db:migrate next.");
} catch {
  const username = userInfo().username;
  const adminUrl = process.env.LOCAL_POSTGRES_URL ?? `postgresql://${encodeURIComponent(username)}@127.0.0.1:5432/postgres`;
  const connection = new URL(adminUrl);
  if (!["localhost", "127.0.0.1", "[::1]"].includes(connection.hostname)) throw new Error("setup:local only supports local PostgreSQL.");
  const pool = new Pool({ connectionString: adminUrl });
  try {
    const existing = await pool.query("SELECT 1 FROM pg_database WHERE datname = $1", ["core_culture_dev"]);
    if (existing.rowCount) throw new Error("core_culture_dev already exists. Configure .env.local yourself; this script will not adopt an existing database.");
    await pool.query('CREATE DATABASE "core_culture_dev"');
    connection.pathname = "/core_culture_dev";
    await writeFile(".env.local", [
      `DATABASE_URL=${connection.toString()}`,
      "BETTER_AUTH_URL=http://127.0.0.1:3000",
      `BETTER_AUTH_SECRET=${randomBytes(48).toString("base64url")}`,
      "MAIL_MODE=outbox",
      "MAIL_FROM=Core Culture <no-reply@example.com>",
      "TRUSTED_IP_HEADER=x-real-ip",
      "",
    ].join("\n"), { flag: "wx", mode: 0o600 });
    console.log("Created isolated core_culture_dev database and private .env.local. No existing databases were modified.");
  } finally { await pool.end(); }
}
