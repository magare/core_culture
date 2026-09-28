import { json, route } from "@/lib/http";
import { listQuery } from "@/lib/validation";
import { listTrainers } from "@/services/club";

export const GET = route(async (request) => {
  const query = listQuery.parse(Object.fromEntries(new URL(request.url).searchParams));
  return json({ trainers: await listTrainers(query), pagination: { limit: query.limit, offset: query.offset } });
});
