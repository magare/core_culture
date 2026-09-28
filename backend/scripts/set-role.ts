import { config } from "dotenv";
import { eq } from "drizzle-orm";

config({ path: ".env.local", quiet: true });
const [email, role] = process.argv.slice(2);
if (!email || role !== "admin") throw new Error("Usage: npm run user:role -- verified-user@example.com admin");
const { db, pool } = await import("../src/db/index");
const { user } = await import("../src/db/schema");
try {
  const [account] = await db.select().from(user).where(eq(user.email, email.toLowerCase()));
  if (!account?.emailVerified) throw new Error("Register and verify this account before granting access.");
  if (account.role === "trainer") throw new Error("Use a dedicated administrator account, not a trainer account.");
  await db.update(user).set({ role: "admin", updatedAt: new Date() }).where(eq(user.id, account.id));
  console.log("Administrator role granted to the specified verified account. Existing sessions read the new role from PostgreSQL.");
} finally { await pool.end(); }
