import { toNextJsHandler } from "better-auth/next-js";
import { z } from "zod";
import { auth } from "@/lib/auth";
import { env } from "@/lib/env";
import { readJson, route } from "@/lib/http";

export const runtime = "nodejs";
const handlers = toNextJsHandler(auth);

export const GET = route(async (request) => handlers.GET(request));
export const POST = route(async (request) => {
  const body = await readJson(request, z.record(z.string(), z.unknown()));
  const headers = new Headers(request.headers);
  headers.delete("content-length");
  // Local callers cannot evade the development limit with spoofed IP headers.
  if (env.isLocal) headers.set(env.TRUSTED_IP_HEADER, "127.0.0.1");
  return handlers.POST(new Request(request.url, { method: "POST", headers, body: JSON.stringify(body) }));
});
