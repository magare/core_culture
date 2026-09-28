import { json, readJson, requireActor, route } from "@/lib/http";
import { trainerInput } from "@/lib/validation";
import { createTrainer } from "@/services/club";

export const POST = route(async (request) => {
  await requireActor(request, ["admin"]);
  return json(await createTrainer(await readJson(request, trainerInput)), 201);
});
