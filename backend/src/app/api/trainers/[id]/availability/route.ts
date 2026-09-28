import { json, readJson, requireActor, route } from "@/lib/http";
import { availabilityWindow, slotInput, uuid } from "@/lib/validation";
import { createSlot, getAvailability } from "@/services/club";

export const GET = route(async (request, context) => {
  const id = uuid.parse((await context.params).id);
  return json(await getAvailability(id, availabilityWindow(new URL(request.url).searchParams)));
});

export const POST = route(async (request, context) => {
  const actor = await requireActor(request, ["trainer", "admin"]);
  const id = uuid.parse((await context.params).id);
  return json(await createSlot(actor, id, await readJson(request, slotInput)), 201);
});
