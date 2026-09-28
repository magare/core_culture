import { json, readJson, requireActor, route } from "@/lib/http";
import { bookingInput, listQuery } from "@/lib/validation";
import { bookSlot, listBookings } from "@/services/club";

export const GET = route(async (request) => {
  const actor = await requireActor(request);
  const query = listQuery.omit({ specialty: true }).parse(Object.fromEntries(new URL(request.url).searchParams));
  return json({ bookings: await listBookings(actor, query), pagination: query });
});

export const POST = route(async (request) => {
  const actor = await requireActor(request, ["member"]);
  const input = await readJson(request, bookingInput);
  const result = await bookSlot(actor, input.slotId);
  return json(result.booking, result.created ? 201 : 200);
});
