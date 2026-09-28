import { betterAuth } from "better-auth";
import { drizzleAdapter } from "@better-auth/drizzle-adapter";
import { after } from "next/server";
import { db } from "@/db";
import * as schema from "@/db/schema";
import { env } from "./env";
import { sendMail } from "./mail";

function deliver(message: Parameters<typeof sendMail>[0]) {
  // Next keeps the task alive after responding, without exposing account
  // existence through SMTP response time. No fire-and-forget promises.
  after(async () => {
    try { await sendMail(message); }
    catch { console.error("Authentication email delivery failed. Check mail provider configuration."); }
  });
}

export const auth = betterAuth({
  appName: "Core Culture",
  baseURL: env.BETTER_AUTH_URL,
  secret: env.BETTER_AUTH_SECRET,
  trustedOrigins: [env.BETTER_AUTH_URL],
  database: drizzleAdapter(db, { provider: "pg", schema, transaction: true }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 12,
    maxPasswordLength: 128,
    requireEmailVerification: true,
    autoSignIn: false,
    revokeSessionsOnPasswordReset: true,
    sendResetPassword: async ({ user, url }) => deliver({
      to: user.email, subject: "Reset your Core Culture password",
      text: `Reset your password using this link:\n${url}\n\nIf you did not request this, ignore this message.`,
    }),
  },
  emailVerification: {
    sendOnSignUp: true,
    autoSignInAfterVerification: false,
    expiresIn: 3600,
    sendVerificationEmail: async ({ user, url }) => deliver({
      to: user.email, subject: "Verify your Core Culture email",
      text: `Verify your email to finish setting up your account:\n${url}\n\nThis link expires in one hour.`,
    }),
  },
  user: {
    additionalFields: {
      role: { type: ["member", "trainer", "admin"], defaultValue: "member", required: false, input: false },
    },
  },
  session: { expiresIn: 60 * 60 * 24 * 7, updateAge: 60 * 60 * 24, cookieCache: { enabled: false } },
  advanced: {
    useSecureCookies: env.BETTER_AUTH_URL.startsWith("https:"),
    ipAddress: { ipAddressHeaders: [env.TRUSTED_IP_HEADER] },
  },
  rateLimit: {
    enabled: true,
    storage: "database",
    window: 60,
    max: 100,
    customRules: {
      "/sign-in/email": { window: 60, max: 10 },
      "/sign-up/email": { window: 60, max: 5 },
      "/request-password-reset": { window: 60, max: 3 },
      "/send-verification-email": { window: 60, max: 3 },
    },
  },
});

export type AuthSession = typeof auth.$Infer.Session;
