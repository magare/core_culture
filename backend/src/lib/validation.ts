import { z } from "zod";

export const uuid = z.string().uuid();
export const trainerInput = z.object({
  userId: z.string().min(1).max(128),
  slug: z.string().min(2).max(80).regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  headline: z.string().trim().min(3).max(100),
  bio: z.string().trim().min(20).max(2000),
  specialties: z.array(z.string().trim().min(2).max(50)).min(1).max(8),
  yearsExperience: z.number().int().min(0).max(80),
}).strict();

export const profileInput = z.object({
  phone: z.string().regex(/^\+[1-9]\d{7,14}$/, "Use international format, e.g. +919876543210").nullable().optional(),
  goal: z.enum(["strength", "fitness", "mobility", "endurance", "general"]).nullable().optional(),
}).strict().refine((value) => Object.keys(value).length > 0, "Provide a profile field to update");

export const selectionInput = z.object({ trainerId: uuid.nullable() }).strict();
export const bookingInput = z.object({ slotId: uuid }).strict();
export const slotInput = z.object({
  startsAt: z.iso.datetime({ offset: true }),
  endsAt: z.iso.datetime({ offset: true }),
}).strict().superRefine((value, context) => {
  const duration = Date.parse(value.endsAt) - Date.parse(value.startsAt);
  if (duration < 15 * 60_000 || duration > 120 * 60_000) {
    context.addIssue({ code: "custom", message: "Slots must last between 15 and 120 minutes", path: ["endsAt"] });
  }
});

export const listQuery = z.object({
  limit: z.coerce.number().int().min(1).max(50).default(20),
  offset: z.coerce.number().int().min(0).max(10_000).default(0),
  specialty: z.string().trim().min(2).max(50).optional(),
}).strict();

export function availabilityWindow(params: URLSearchParams, now = new Date()) {
  const value = z.object({
    from: z.iso.datetime({ offset: true }).optional(),
    to: z.iso.datetime({ offset: true }).optional(),
  }).strict().parse(Object.fromEntries(params));
  const from = value.from ? new Date(value.from) : now;
  const to = value.to ? new Date(value.to) : new Date(from.getTime() + 14 * 86400_000);
  if (to <= from || to.getTime() - from.getTime() > 31 * 86400_000) {
    throw new z.ZodError([{ code: "custom", path: ["to"], message: "Availability range must be between 0 and 31 days" }]);
  }
  return { from: from < now ? now : from, to };
}
