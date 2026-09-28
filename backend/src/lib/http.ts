import { randomUUID } from "node:crypto";
import { z } from "zod";
import { sql } from "drizzle-orm";
import { db } from "@/db";
import { rateLimit } from "@/db/schema";
import { auth, type AuthSession } from "./auth";
import { env } from "./env";
import { ApiError, databaseCode } from "./errors";

export type Actor = AuthSession["user"];
export type RouteContext = { params: Promise<Record<string, string | string[]>> };
type Handler = (request: Request, context: RouteContext) => Promise<Response>;

export function json(data: unknown, status = 200) {
  return Response.json({ data }, { status, headers: { "Cache-Control": "no-store" } });
}

export function assertSameOrigin(request: Request) {
  if (request.headers.get("origin") !== env.BETTER_AUTH_URL || request.headers.get("sec-fetch-site") === "cross-site") {
    throw new ApiError(403, "INVALID_ORIGIN", "Requests must come from this application's origin.");
  }
}

export async function readJson<T>(request: Request, schema: z.ZodType<T>): Promise<T> {
  if (request.headers.get("content-type")?.split(";")[0].trim() !== "application/json") {
    throw new ApiError(415, "JSON_REQUIRED", "Send an application/json request.");
  }
  const reader = request.body?.getReader();
  if (!reader) throw new ApiError(400, "INVALID_JSON", "Request body is required.");
  let size = 0;
  const chunks: Uint8Array[] = [];
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 16_384) {
        await reader.cancel();
        throw new ApiError(413, "BODY_TOO_LARGE", "Request body must be smaller than 16 KB.");
      }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  let body: unknown;
  try { body = JSON.parse(Buffer.concat(chunks).toString("utf8")); }
  catch { throw new ApiError(400, "INVALID_JSON", "Request body is not valid JSON."); }
  return schema.parse(body);
}

export async function requireActor(request: Request, roles?: Actor["role"][]): Promise<Actor> {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session) throw new ApiError(401, "UNAUTHENTICATED", "Sign in to continue.");
  if (!session.user.emailVerified) throw new ApiError(403, "EMAIL_NOT_VERIFIED", "Verify your email to continue.");
  if (roles && !roles.includes(session.user.role)) throw new ApiError(403, "FORBIDDEN", "You do not have permission for this action.");
  if (!["GET", "HEAD", "OPTIONS"].includes(request.method)) {
    // Atomic, shared-database limit for application writes, keyed by account.
    const now = Date.now();
    const [counter] = await db.insert(rateLimit).values({
      id: randomUUID(), key: `app-write:${session.user.id}`, count: 1, lastRequest: now,
    }).onConflictDoUpdate({ target: rateLimit.key, set: {
      count: sql`CASE WHEN ${rateLimit.lastRequest} < ${now - 60_000} THEN 1 ELSE ${rateLimit.count} + 1 END`,
      lastRequest: sql`CASE WHEN ${rateLimit.lastRequest} < ${now - 60_000} THEN ${now} ELSE ${rateLimit.lastRequest} END`,
    } }).returning();
    if (counter.count > 30) throw new ApiError(429, "RATE_LIMITED", "Too many changes. Try again in a minute.");
  }
  return session.user;
}

export function route(handler: Handler): Handler {
  return async (request, context) => {
    const requestId = randomUUID();
    try {
      if (!["GET", "HEAD", "OPTIONS"].includes(request.method)) assertSameOrigin(request);
      const response = await handler(request, context);
      response.headers.set("Cache-Control", "no-store");
      response.headers.set("X-Request-Id", requestId);
      return response;
    } catch (error) {
      let status = 500, code = "INTERNAL_ERROR", message = "Something went wrong. Please try again.";
      let issues: { field: string; message: string }[] | undefined;
      if (error instanceof ApiError) ({ status, code, message } = error);
      else if (error instanceof z.ZodError) {
        status = 422; code = "VALIDATION_ERROR"; message = "Check the supplied fields.";
        issues = error.issues.map((issue) => ({ field: issue.path.join("."), message: issue.message }));
      } else if (["23505", "23P01"].includes(databaseCode(error) ?? "")) {
        status = 409; code = "CONFLICT"; message = "This record or time slot is no longer available.";
      } else {
        // Deliberately exclude SQL, request bodies, passwords and personal data.
        console.error({ requestId, error: "Unhandled API error", databaseCode: databaseCode(error) });
      }
      return Response.json({ error: { code, message, ...(issues ? { issues } : {}), requestId } }, {
        status, headers: { "Cache-Control": "no-store", "X-Request-Id": requestId, ...(status === 429 ? { "Retry-After": "60" } : {}) },
      });
    }
  };
}
