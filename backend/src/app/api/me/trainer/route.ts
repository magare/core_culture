import { json, readJson, requireActor, route } from "@/lib/http";
import { selectionInput } from "@/lib/validation";
import { selectTrainer } from "@/services/club";

export const PUT = route(async (request) => {
  const actor = await requireActor(request, ["member"]);
  const input = await readJson(request, selectionInput);
  return json(await selectTrainer(actor, input.trainerId));
});
