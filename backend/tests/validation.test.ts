import { test } from "node:test";
import assert from "node:assert/strict";
import { availabilityWindow, bookingInput, listQuery, profileInput, selectionInput, slotInput, trainerInput } from "../src/lib/validation";

test("profile accepts a valid international phone and defined goal", () => {
  assert.deepEqual(profileInput.parse({ phone: "+919876543210", goal: "strength" }), { phone: "+919876543210", goal: "strength" });
  assert.deepEqual(profileInput.parse({ phone: null }), { phone: null });
});
test("profile rejects mass assignment, invalid phone and empty patches", () => {
  for (const input of [{ role: "admin" }, { phone: "1234" }, {}, { userId: "someone-else" }]) assert.equal(profileInput.safeParse(input).success, false);
});
test("booking accepts only a UUID slot, not client-supplied prices or identities", () => {
  const slotId = "15e969cf-a69d-4ef8-a0fa-28df94679e5b";
  assert.deepEqual(bookingInput.parse({ slotId }), { slotId });
  assert.equal(bookingInput.safeParse({ slotId, memberId: "other" }).success, false);
  assert.equal(bookingInput.safeParse({ slotId, startsAt: "2030-01-01" }).success, false);
});
test("trainer selection can be cleared but cannot reference an invalid UUID", () => {
  assert.deepEqual(selectionInput.parse({ trainerId: null }), { trainerId: null });
  assert.equal(selectionInput.safeParse({ trainerId: "invalid" }).success, false);
});
test("slots require timezone-aware dates and a 15–120 minute duration", () => {
  assert.equal(slotInput.safeParse({ startsAt: "2030-01-01T10:00:00+05:30", endsAt: "2030-01-01T11:00:00+05:30" }).success, true);
  for (const endsAt of ["2030-01-01T10:01:00Z", "2030-01-01T09:00:00Z", "2030-01-01T13:00:00Z"]) {
    assert.equal(slotInput.safeParse({ startsAt: "2030-01-01T10:00:00Z", endsAt }).success, false);
  }
  assert.equal(slotInput.safeParse({ startsAt: "2030-01-01T10:00:00", endsAt: "2030-01-01T11:00:00" }).success, false);
});
test("list pagination is bounded and defaults are predictable", () => {
  assert.deepEqual(listQuery.parse({}), { limit: 20, offset: 0 });
  for (const input of [{ limit: "0" }, { limit: "100000" }, { offset: "-1" }, { sort: "anything" }]) assert.equal(listQuery.safeParse(input).success, false);
});
test("availability defaults to fourteen days and caps queries at 31 days", () => {
  const now = new Date("2030-01-01T00:00:00Z");
  assert.equal(availabilityWindow(new URLSearchParams(), now).to.toISOString(), "2030-01-15T00:00:00.000Z");
  assert.throws(() => availabilityWindow(new URLSearchParams({ from: now.toISOString(), to: "2030-03-01T00:00:00Z" }), now));
  assert.throws(() => availabilityWindow(new URLSearchParams({ from: now.toISOString(), to: now.toISOString() }), now));
});
test("trainer payload excludes permission flags", () => {
  assert.equal(trainerInput.safeParse({ userId: "123", slug: "test-coach", headline: "Strength coach", bio: "A test biography for a trainer.", specialties: ["Strength"], yearsExperience: 8 }).success, true);
  assert.equal(trainerInput.safeParse({ role: "admin" }).success, false);
});
