import { json, readJson, requireActor, route } from "@/lib/http";
import { profileInput } from "@/lib/validation";
import { getProfile, updateProfile } from "@/services/club";

export const GET = route(async (request) => json(await getProfile(await requireActor(request))));
export const PATCH = route(async (request) => {
  const actor = await requireActor(request, ["member"]);
  return json(await updateProfile(actor, await readJson(request, profileInput)));
});
