import { and, arrayContains, asc, desc, eq, gt, gte, isNull, lt } from "drizzle-orm";
import { db } from "@/db";
import { bookings, memberProfiles, trainerSlots, trainers, user } from "@/db/schema";
import { ApiError } from "@/lib/errors";
import type { Actor } from "@/lib/http";
import type { z } from "zod";
import type { profileInput, trainerInput } from "@/lib/validation";

const trainerFields = {
  id: trainers.id, name: user.name, slug: trainers.slug, headline: trainers.headline,
  bio: trainers.bio, specialties: trainers.specialties, yearsExperience: trainers.yearsExperience,
};

export async function listTrainers(options: { limit: number; offset: number; specialty?: string }) {
  return db.select(trainerFields).from(trainers).innerJoin(user, eq(trainers.userId, user.id))
    .where(and(eq(trainers.active, true), options.specialty ? arrayContains(trainers.specialties, [options.specialty]) : undefined))
    .orderBy(asc(user.name), asc(trainers.id)).limit(options.limit).offset(options.offset);
}

export async function getTrainer(id: string) {
  const [trainer] = await db.select(trainerFields).from(trainers).innerJoin(user, eq(trainers.userId, user.id))
    .where(and(eq(trainers.id, id), eq(trainers.active, true)));
  if (!trainer) throw new ApiError(404, "TRAINER_NOT_FOUND", "Trainer not found.");
  return trainer;
}

export async function getAvailability(id: string, window: { from: Date; to: Date }) {
  await getTrainer(id);
  return db.select({ id: trainerSlots.id, trainerId: trainerSlots.trainerId, startsAt: trainerSlots.startsAt, endsAt: trainerSlots.endsAt })
    .from(trainerSlots).leftJoin(bookings, and(eq(bookings.slotId, trainerSlots.id), eq(bookings.status, "confirmed")))
    .where(and(eq(trainerSlots.trainerId, id), isNull(trainerSlots.cancelledAt), isNull(bookings.id),
      gte(trainerSlots.startsAt, window.from), lt(trainerSlots.startsAt, window.to)))
    .orderBy(asc(trainerSlots.startsAt)).limit(200);
}

export async function getProfile(actor: Actor) {
  const [profile] = await db.select().from(memberProfiles).where(eq(memberProfiles.userId, actor.id));
  return { user: { id: actor.id, name: actor.name, email: actor.email, role: actor.role }, profile: profile ?? {
    userId: actor.id, phone: null, goal: null, selectedTrainerId: null,
  } };
}

export async function updateProfile(actor: Actor, input: z.infer<typeof profileInput>) {
  const [profile] = await db.insert(memberProfiles).values({ userId: actor.id, ...input })
    .onConflictDoUpdate({ target: memberProfiles.userId, set: { ...input, updatedAt: new Date() } }).returning();
  return profile;
}

export async function selectTrainer(actor: Actor, trainerId: string | null) {
  if (trainerId) await getTrainer(trainerId);
  const [profile] = await db.insert(memberProfiles).values({ userId: actor.id, selectedTrainerId: trainerId })
    .onConflictDoUpdate({ target: memberProfiles.userId, set: { selectedTrainerId: trainerId, updatedAt: new Date() } }).returning();
  return profile;
}

export async function createTrainer(input: z.infer<typeof trainerInput>) {
  return db.transaction(async (tx) => {
    const [account] = await tx.select().from(user).where(eq(user.id, input.userId)).for("update");
    if (!account) throw new ApiError(404, "USER_NOT_FOUND", "The trainer must register an account first.");
    if (!account.emailVerified) throw new ApiError(409, "EMAIL_NOT_VERIFIED", "The account must verify its email first.");
    if (account.role === "admin") throw new ApiError(409, "ROLE_CONFLICT", "Use a dedicated trainer account.");
    await tx.update(user).set({ role: "trainer", updatedAt: new Date() }).where(eq(user.id, input.userId));
    const [trainer] = await tx.insert(trainers).values(input).returning();
    return trainer;
  });
}

async function assertTrainerOwner(actor: Actor, trainerId: string) {
  const [trainer] = await db.select().from(trainers).where(eq(trainers.id, trainerId));
  if (!trainer || !trainer.active) throw new ApiError(404, "TRAINER_NOT_FOUND", "Trainer not found.");
  if (actor.role !== "admin" && trainer.userId !== actor.id) throw new ApiError(403, "FORBIDDEN", "You can only manage your own availability.");
  return trainer;
}

export async function createSlot(actor: Actor, trainerId: string, input: { startsAt: string; endsAt: string }) {
  await assertTrainerOwner(actor, trainerId);
  const startsAt = new Date(input.startsAt), endsAt = new Date(input.endsAt);
  if (startsAt.getTime() < Date.now() + 5 * 60_000 || startsAt.getTime() > Date.now() + 90 * 86400_000) {
    throw new ApiError(422, "INVALID_SLOT_TIME", "Publish slots from five minutes to 90 days in advance.");
  }
  const [slot] = await db.insert(trainerSlots).values({ trainerId, startsAt, endsAt }).returning();
  return slot;
}

export async function withdrawSlot(actor: Actor, trainerId: string, slotId: string) {
  await assertTrainerOwner(actor, trainerId);
  return db.transaction(async (tx) => {
    const [slot] = await tx.select().from(trainerSlots).where(and(eq(trainerSlots.id, slotId), eq(trainerSlots.trainerId, trainerId))).for("update");
    if (!slot) throw new ApiError(404, "SLOT_NOT_FOUND", "Slot not found.");
    const [booking] = await tx.select({ id: bookings.id }).from(bookings).where(and(eq(bookings.slotId, slotId), eq(bookings.status, "confirmed")));
    if (booking) throw new ApiError(409, "SLOT_BOOKED", "Cancel the booking before withdrawing its slot.");
    if (slot.cancelledAt) return slot;
    const [updated] = await tx.update(trainerSlots).set({ cancelledAt: new Date() }).where(eq(trainerSlots.id, slotId)).returning();
    return updated;
  });
}

export async function bookSlot(actor: Actor, slotId: string) {
  return db.transaction(async (tx) => {
    // Serialize contenders for this slot. Independent slots are protected by the
    // member/trainer GiST exclusions in PostgreSQL, not a check-then-insert race.
    const [slot] = await tx.select().from(trainerSlots).where(eq(trainerSlots.id, slotId)).for("update");
    if (!slot || slot.cancelledAt) throw new ApiError(404, "SLOT_NOT_FOUND", "This slot is no longer available.");
    if (slot.startsAt <= new Date()) throw new ApiError(409, "SLOT_PAST", "This session has already started.");
    const [trainer] = await tx.select().from(trainers).where(and(eq(trainers.id, slot.trainerId), eq(trainers.active, true)));
    if (!trainer) throw new ApiError(409, "TRAINER_UNAVAILABLE", "This trainer is unavailable.");
    const [existing] = await tx.select().from(bookings).where(and(eq(bookings.slotId, slotId), eq(bookings.status, "confirmed")));
    if (existing?.memberId === actor.id) return { booking: existing, created: false };
    if (existing) throw new ApiError(409, "SLOT_BOOKED", "Another member has booked this slot.");
    const [booking] = await tx.insert(bookings).values({ memberId: actor.id, slotId,
      trainerId: slot.trainerId, startsAt: slot.startsAt, endsAt: slot.endsAt }).returning();
    return { booking, created: true };
  });
}

export async function listBookings(actor: Actor, options: { limit: number; offset: number }) {
  const owner = actor.role === "admin" ? undefined
    : actor.role === "trainer" ? eq(trainers.userId, actor.id) : eq(bookings.memberId, actor.id);
  return db.select({
    id: bookings.id, memberId: bookings.memberId, slotId: bookings.slotId, trainerId: bookings.trainerId,
    trainerName: user.name, startsAt: bookings.startsAt, endsAt: bookings.endsAt,
    status: bookings.status, cancelledAt: bookings.cancelledAt, createdAt: bookings.createdAt,
  }).from(bookings).innerJoin(trainers, eq(trainers.id, bookings.trainerId)).innerJoin(user, eq(user.id, trainers.userId))
    .where(owner).orderBy(desc(bookings.startsAt), desc(bookings.id)).limit(options.limit).offset(options.offset);
}

export async function cancelBooking(actor: Actor, bookingId: string) {
  const [booking] = await db.select({ record: bookings, trainerUserId: trainers.userId }).from(bookings)
    .innerJoin(trainers, eq(bookings.trainerId, trainers.id)).where(eq(bookings.id, bookingId));
  const ownsBooking = booking && (actor.role === "admin" || booking.record.memberId === actor.id ||
    (actor.role === "trainer" && booking.trainerUserId === actor.id));
  if (!booking || !ownsBooking) throw new ApiError(404, "BOOKING_NOT_FOUND", "Booking not found.");
  if (booking.record.status === "cancelled") return booking.record;
  const [cancelled] = await db.update(bookings).set({ status: "cancelled", cancelledAt: new Date(), updatedAt: new Date() })
    .where(and(eq(bookings.id, bookingId), eq(bookings.status, "confirmed"), gt(bookings.startsAt, new Date()))).returning();
  if (!cancelled) {
    const [current] = await db.select().from(bookings).where(eq(bookings.id, bookingId));
    if (current?.status === "cancelled") return current;
    throw new ApiError(409, "BOOKING_STARTED", "Sessions cannot be cancelled after their start time.");
  }
  return cancelled;
}
