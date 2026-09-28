import { z } from "zod";

const schema = z.object({
  DATABASE_URL: z.string().url().refine((value) => /^postgres(ql)?:/.test(value)),
  BETTER_AUTH_URL: z.string().url(),
  BETTER_AUTH_SECRET: z.string().min(32).refine((value) => !value.includes("replace-")),
  MAIL_MODE: z.enum(["outbox", "smtp"]).default("outbox"),
  MAIL_FROM: z.string().min(1).default("Core Culture <no-reply@example.com>"),
  MAIL_OUTBOX_DIR: z.string().default(".local/mail"),
  SMTP_URL: z.string().url().optional(),
  TRUSTED_IP_HEADER: z.string().regex(/^[a-z0-9-]+$/).default("x-real-ip"),
});

const parsed = schema.safeParse(process.env);
if (!parsed.success) {
  // Report field names only: database URLs and auth secrets must never enter logs.
  throw new Error(`Invalid backend configuration: ${parsed.error.issues.map((issue) => issue.path.join(".")).join(", ")}. See .env.example.`);
}
const values = parsed.data;
const url = new URL(values.BETTER_AUTH_URL);
const local = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
if (url.origin !== values.BETTER_AUTH_URL) throw new Error("BETTER_AUTH_URL must be an origin without a path or trailing slash.");
if (!local && (url.protocol !== "https:" || values.MAIL_MODE !== "smtp")) {
  throw new Error("Public deployments require HTTPS and MAIL_MODE=smtp.");
}
if (values.MAIL_MODE === "smtp" && !values.SMTP_URL) throw new Error("SMTP_URL is required for SMTP delivery.");

export const env = { ...values, isLocal: local };
