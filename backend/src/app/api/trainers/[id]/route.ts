import { json, route } from "@/lib/http";
import { uuid } from "@/lib/validation";
import { getTrainer } from "@/services/club";

export const GET = route(async (_request, context) => json(await getTrainer(uuid.parse((await context.params).id))));
