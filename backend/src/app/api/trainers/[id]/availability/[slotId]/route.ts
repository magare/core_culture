import { json, requireActor, route } from "@/lib/http";
import { uuid } from "@/lib/validation";
import { withdrawSlot } from "@/services/club";

export const DELETE = route(async (request, context) => {
  const actor = await requireActor(request, ["trainer", "admin"]);
  const params = await context.params;
  return json(await withdrawSlot(actor, uuid.parse(params.id), uuid.parse(params.slotId)));
});
