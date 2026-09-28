import { sql } from "drizzle-orm";
import { bigint, boolean, check, index, integer, pgEnum, pgTable, text, timestamp, uniqueIndex, uuid } from "drizzle-orm/pg-core";

const time = (name: string) => timestamp(name, { withTimezone: true });
const audit = () => ({ createdAt: time("created_at").defaultNow().notNull(), updatedAt: time("updated_at").defaultNow().notNull() });

export const roleEnum = pgEnum("user_role", ["member", "trainer", "admin"]);
export const bookingStatusEnum = pgEnum("booking_status", ["confirmed", "cancelled"]);

// Better Auth owns credentials, sessions, verification tokens and password hashing.
export const user = pgTable("users", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").default(false).notNull(),
  image: text("image"),
  role: roleEnum("role").default("member").notNull(),
  ...audit(),
}, (table) => [uniqueIndex("users_email_lower_unique").on(sql`lower(${table.email})`)]);

export const session = pgTable("sessions", {
  id: text("id").primaryKey(),
  userId: text("user_id").references(() => user.id, { onDelete: "cascade" }).notNull(),
  token: text("token").unique().notNull(),
  expiresAt: time("expires_at").notNull(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  ...audit(),
}, (table) => [index("sessions_user_idx").on(table.userId), index("sessions_expiry_idx").on(table.expiresAt)]);

export const account = pgTable("accounts", {
  id: text("id").primaryKey(),
  userId: text("user_id").references(() => user.id, { onDelete: "cascade" }).notNull(),
  accountId: text("account_id").notNull(),
  providerId: text("provider_id").notNull(),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  idToken: text("id_token"),
  accessTokenExpiresAt: time("access_token_expires_at"),
  refreshTokenExpiresAt: time("refresh_token_expires_at"),
  scope: text("scope"),
  password: text("password"),
  ...audit(),
}, (table) => [index("accounts_user_idx").on(table.userId), uniqueIndex("accounts_provider_unique").on(table.providerId, table.accountId)]);

export const verification = pgTable("verifications", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: time("expires_at").notNull(),
  ...audit(),
}, (table) => [index("verifications_identifier_idx").on(table.identifier)]);

export const rateLimit = pgTable("rate_limits", {
  id: text("id").primaryKey(),
  key: text("key").unique().notNull(),
  count: integer("count").notNull(),
  lastRequest: bigint("last_request", { mode: "number" }).notNull(),
});

export const trainers = pgTable("trainers", {
  id: uuid("id").defaultRandom().primaryKey(),
  userId: text("user_id").references(() => user.id, { onDelete: "restrict" }).unique().notNull(),
  slug: text("slug").unique().notNull(),
  headline: text("headline").notNull(),
  bio: text("bio").notNull(),
  specialties: text("specialties").array().notNull(),
  yearsExperience: integer("years_experience").default(0).notNull(),
  active: boolean("active").default(true).notNull(),
  ...audit(),
}, (table) => [check("trainers_experience_valid", sql`${table.yearsExperience} BETWEEN 0 AND 80`)]);

export const memberProfiles = pgTable("member_profiles", {
  userId: text("user_id").references(() => user.id, { onDelete: "cascade" }).primaryKey(),
  phone: text("phone"),
  goal: text("goal"),
  selectedTrainerId: uuid("selected_trainer_id").references(() => trainers.id, { onDelete: "set null" }),
  ...audit(),
});

// Availability is a concrete, immutable time slot, not a recurrence rule.
export const trainerSlots = pgTable("trainer_slots", {
  id: uuid("id").defaultRandom().primaryKey(),
  trainerId: uuid("trainer_id").references(() => trainers.id, { onDelete: "restrict" }).notNull(),
  startsAt: time("starts_at").notNull(),
  endsAt: time("ends_at").notNull(),
  cancelledAt: time("cancelled_at"),
  createdAt: time("created_at").defaultNow().notNull(),
}, (table) => [
  index("slots_trainer_start_idx").on(table.trainerId, table.startsAt),
  check("slots_duration_valid", sql`${table.endsAt} - ${table.startsAt} BETWEEN interval '15 minutes' AND interval '2 hours'`),
]);

export const bookings = pgTable("bookings", {
  id: uuid("id").defaultRandom().primaryKey(),
  memberId: text("member_id").references(() => user.id, { onDelete: "restrict" }).notNull(),
  slotId: uuid("slot_id").references(() => trainerSlots.id, { onDelete: "restrict" }).notNull(),
  trainerId: uuid("trainer_id").references(() => trainers.id, { onDelete: "restrict" }).notNull(),
  startsAt: time("starts_at").notNull(),
  endsAt: time("ends_at").notNull(),
  status: bookingStatusEnum("status").default("confirmed").notNull(),
  cancelledAt: time("cancelled_at"),
  ...audit(),
}, (table) => [
  index("bookings_member_start_idx").on(table.memberId, table.startsAt),
  index("bookings_trainer_start_idx").on(table.trainerId, table.startsAt),
  uniqueIndex("bookings_one_active_slot").on(table.slotId).where(sql`${table.status} = 'confirmed'`),
  check("bookings_time_valid", sql`${table.endsAt} > ${table.startsAt}`),
  check("bookings_cancellation_valid", sql`(${table.status} = 'cancelled') = (${table.cancelledAt} IS NOT NULL)`),
]);

// GiST exclusions and booking/slot consistency triggers live in the custom SQL
// migration: Drizzle cannot express those PostgreSQL constraints in its schema.
