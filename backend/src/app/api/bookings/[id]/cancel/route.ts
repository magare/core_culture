import { json, requireActor, route } from "@/lib/http";
import { uuid } from "@/lib/validation";
import { cancelBooking } from "@/services/club";

export const POST = route(async (request, context) => {
  const actor = await requireActor(request);
  return json(await cancelBooking(actor, uuid.parse((await context.params).id)));
});
