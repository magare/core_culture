import { after, before, beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { Pool } from "pg";

if (process.env.INTEGRATION_TEST !== "1" || !new URL(process.env.DATABASE_URL!).pathname.match(/^\/core_culture_test_[a-f0-9]{12}$/)) {
  throw new Error("Run npm run test:integration. Never point these tests at a real application database.");
}
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const base = process.env.BETTER_AUTH_URL!;
const password = "Only-for-integration-tests-41!";
type Fixture = { id: string; email: string; cookie: string };
type Trainer = { id: string; name: string; specialties: string[] };
type Slot = { id: string; trainerId: string; startsAt: string; endsAt: string };
type Booking = { id: string; memberId: string; status: string; slotId: string };
type ErrorBody = { error: { code: string; message: string } };
let member: Fixture, other: Fixture, admin: Fixture, trainerAccount: Fixture, secondTrainerAccount: Fixture;
let trainer: Trainer, secondTrainer: Trainer;

async function api<T = ErrorBody>(url: string, options: { method?: string; body?: unknown; cookie?: string; origin?: string; headers?: Record<string, string> } = {}) {
  const headers: Record<string, string> = { "Content-Type": "application/json", Origin: options.origin ?? base, ...options.headers };
  if (options.cookie) headers.Cookie = options.cookie;
  const response = await fetch(`${base}${url}`, { method: options.method ?? "GET", headers,
    ...(options.body === undefined ? {} : { body: JSON.stringify(options.body) }), redirect: "manual" });
  const body = await response.json() as T;
  return { response, body };
}

async function mailLink(email: string, subject: string) {
  for (let attempt = 0; attempt < 40; attempt++) {
    const names = await readdir(process.env.MAIL_OUTBOX_DIR!).catch(() => [] as string[]);
    for (const name of names.reverse()) {
      const message = JSON.parse(await readFile(path.join(process.env.MAIL_OUTBOX_DIR!, name), "utf8")) as { to: string; subject: string; text: string };
      if (message.to === email && message.subject.includes(subject)) {
        const url = message.text.match(/https?:\/\/\S+/)?.[0];
        if (url) return url;
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error("Expected local verification/recovery email was not created.");
}

async function signIn(email: string, secret = password) {
  const result = await api("/api/auth/sign-in/email", { method: "POST", body: { email, password: secret } });
  assert.equal(result.response.status, 200, "Sign-in should succeed after verification");
  const cookies = result.response.headers.getSetCookie();
  assert.ok(cookies.some((cookie) => /httponly/i.test(cookie)));
  return cookies.map((cookie) => cookie.split(";")[0]).join("; ");
}

async function register(label: string): Promise<Fixture> {
  const email = `${label}@example.invalid`;
  const registration = await api("/api/auth/sign-up/email", { method: "POST", body: { name: `Test ${label}`, email, password, role: "admin" } });
  assert.equal(registration.response.status, 200);
  const record = (await pool.query("SELECT id, role, email_verified FROM users WHERE email = $1", [email])).rows[0];
  assert.equal(record.role, "member", "Public registration must not permit role escalation");
  assert.equal(record.email_verified, false);
  const url = await mailLink(email, "Verify");
  const verified = await fetch(url, { redirect: "manual" });
  assert.ok([200, 302].includes(verified.status));
  return { id: record.id, email, cookie: await signIn(email) };
}

async function publish(account: Fixture, trainerId: string, hours: number, duration = 60) {
  const startsAt = new Date(Date.now() + hours * 3600_000);
  startsAt.setUTCSeconds(0, 0);
  return api<{ data: Slot }>(`/api/trainers/${trainerId}/availability`, { method: "POST", cookie: account.cookie,
    body: { startsAt: startsAt.toISOString(), endsAt: new Date(startsAt.getTime() + duration * 60_000).toISOString() } });
}

before(async () => {
  member = await register("member"); other = await register("other"); admin = await register("admin");
  trainerAccount = await register("trainer"); secondTrainerAccount = await register("second-trainer");
  await pool.query("UPDATE users SET role = 'admin' WHERE id = $1", [admin.id]);
  for (const [account, slug] of [[trainerAccount, "test-strength"], [secondTrainerAccount, "test-mobility"]] as const) {
    const result = await api<{ data: Trainer }>("/api/admin/trainers", { method: "POST", cookie: admin.cookie, body: {
      userId: account.id, slug, headline: "A test trainer", bio: "A fictional trainer used only in integration testing.", specialties: ["Strength"], yearsExperience: 6,
    } });
    assert.equal(result.response.status, 201);
    if (account === trainerAccount) trainer = result.body.data; else secondTrainer = result.body.data;
  }
});
beforeEach(async () => { await pool.query("DELETE FROM rate_limits"); });
after(async () => { await pool.end(); });

test("health, platform and account page run in Next.js", async () => {
  const health = await api<{ status: string }>("/api/health");
  assert.equal(health.body.status, "ok");
  for (const route of ["/", "/account"]) {
    const response = await fetch(`${base}${route}`); assert.equal(response.status, 200);
    assert.match(await response.text(), /CORE CULTURE/);
  }
});
test("protected endpoints reject unauthenticated requests", async () => {
  assert.equal((await api("/api/me")).response.status, 401);
  assert.equal((await api("/api/bookings", { method: "POST", body: { slotId: randomUUID() } })).response.status, 401);
});
test("registration rejects weak passwords and requires email verification", async () => {
  assert.equal((await api("/api/auth/sign-up/email", { method: "POST", body: { email: "weak@example.invalid", name: "Weak", password: "short" } })).response.status, 400);
  const email = "unverified@example.invalid";
  assert.equal((await api("/api/auth/sign-up/email", { method: "POST", body: { email, name: "Unverified", password } })).response.status, 200);
  assert.equal((await api("/api/auth/sign-in/email", { method: "POST", body: { email, password } })).response.status, 403);
});
test("duplicate registration does not disclose account existence", async () => {
  const duplicate = await api("/api/auth/sign-up/email", { method: "POST", body: { email: member.email, name: "Duplicate", password } });
  assert.equal(duplicate.response.status, 200);
  assert.equal((await pool.query("SELECT count(*) FROM users WHERE email = $1", [member.email])).rows[0].count, "1");
});
test("authentication rate limits remain enabled", async () => {
  const responses = [];
  for (let attempt = 0; attempt < 11; attempt++) responses.push((await api("/api/auth/sign-in/email", { method: "POST", body: { email: member.email, password: "wrong-password-value" } })).response.status);
  assert.ok(responses.slice(0, 10).every((status) => status === 401));
  assert.equal(responses[10], 429);
});
test("profile updates persist without allowing mass assignment or role changes", async () => {
  assert.equal((await api("/api/me", { method: "PATCH", cookie: member.cookie, body: { role: "admin" } })).response.status, 422);
  const update = await api<{ data: { phone: string; goal: string } }>("/api/me", { method: "PATCH", cookie: member.cookie, body: { phone: "+919876543210", goal: "strength" } });
  assert.equal(update.response.status, 200); assert.equal(update.body.data.phone, "+919876543210");
  const me = await api<{ data: { user: { role: string }; profile: { goal: string } } }>("/api/me", { cookie: member.cookie });
  assert.equal(me.body.data.profile.goal, "strength"); assert.equal(me.body.data.user.role, "member");
  assert.match(me.response.headers.get("cache-control")!, /no-store/);
});
test("authentication updates cannot promote roles and passwords are hashed", async () => {
  await api("/api/auth/update-user", { method: "POST", cookie: member.cookie, body: { role: "admin", name: "Updated test name" } });
  const user = (await pool.query("SELECT role FROM users WHERE id = $1", [member.id])).rows[0];
  const account = (await pool.query("SELECT password FROM accounts WHERE user_id = $1", [member.id])).rows[0];
  assert.equal(user.role, "member"); assert.ok(account.password); assert.notEqual(account.password, password);
});
test("cross-origin and missing-origin writes are denied", async () => {
  const cross = await api("/api/me", { method: "PATCH", cookie: member.cookie, body: { goal: "mobility" }, origin: "https://evil.example" });
  assert.equal(cross.response.status, 403); assert.equal(cross.body.error.code, "INVALID_ORIGIN");
  const missing = await fetch(`${base}/api/me`, { method: "PATCH", headers: { "Content-Type": "application/json", Cookie: member.cookie }, body: "{}" });
  assert.equal(missing.status, 403);
  assert.equal((await api("/api/auth/sign-out", { method: "POST", cookie: member.cookie, body: {}, origin: "https://evil.example" })).response.status, 403);
});
test("validation rejects malformed IDs, dates, oversized bodies and non-JSON input", async () => {
  assert.equal((await api("/api/trainers/not-a-uuid")).response.status, 422);
  assert.equal((await api("/api/trainers?limit=50000")).response.status, 422);
  assert.equal((await api(`/api/trainers/${trainer.id}/availability?to=not-a-date`)).response.status, 422);
  assert.equal((await api("/api/me", { method: "PATCH", cookie: member.cookie, body: { goal: "x".repeat(17000) } })).response.status, 413);
  assert.equal((await api("/api/me", { method: "PATCH", cookie: member.cookie, body: {}, headers: { "Content-Type": "text/plain" } })).response.status, 415);
  const malformed = await fetch(`${base}/api/me`, { method: "PATCH", headers: { Origin: base, "Content-Type": "application/json", Cookie: member.cookie }, body: "{" });
  assert.equal(malformed.status, 400);
});
test("public trainer API omits private account fields and supports filters", async () => {
  const result = await api<{ data: { trainers: Trainer[] } }>("/api/trainers?specialty=Strength&limit=1");
  assert.equal(result.body.data.trainers.length, 1);
  assert.equal("email" in result.body.data.trainers[0], false);
  assert.equal("userId" in result.body.data.trainers[0], false);
  assert.equal((await api(`/api/trainers/${randomUUID()}`)).response.status, 404);
});
test("members select, change and clear their preferred trainer", async () => {
  for (const trainerId of [trainer.id, secondTrainer.id, null]) {
    const result = await api<{ data: { selectedTrainerId: string | null } }>("/api/me/trainer", { method: "PUT", cookie: member.cookie, body: { trainerId } });
    assert.equal(result.response.status, 200); assert.equal(result.body.data.selectedTrainerId, trainerId);
  }
  assert.equal((await api("/api/me/trainer", { method: "PUT", cookie: member.cookie, body: { trainerId: randomUUID() } })).response.status, 404);
});
test("only administrators can create trainer profiles", async () => {
  assert.equal((await api("/api/admin/trainers", { method: "POST", cookie: member.cookie, body: {} })).response.status, 403);
  assert.equal((await api("/api/admin/trainers", { method: "POST", cookie: trainerAccount.cookie, body: {} })).response.status, 403);
});
test("trainers can publish their own slots but cannot edit another trainer", async () => {
  const own = await publish(trainerAccount, trainer.id, 24); assert.equal(own.response.status, 201);
  assert.equal((await publish(trainerAccount, secondTrainer.id, 24)).response.status, 403);
  assert.equal((await publish(member, trainer.id, 25)).response.status, 403);
  assert.equal((await publish(trainerAccount, trainer.id, -1)).response.status, 422);
  assert.equal((await publish(trainerAccount, trainer.id, 25, 10)).response.status, 422);
});
test("PostgreSQL rejects overlapping availability but allows adjacent slots", async () => {
  assert.equal((await publish(trainerAccount, trainer.id, 48)).response.status, 201);
  assert.equal((await publish(trainerAccount, trainer.id, 48.5)).response.status, 409);
  assert.equal((await publish(trainerAccount, trainer.id, 49)).response.status, 201);
});
test("concurrent requests for one slot produce exactly one booking", async () => {
  const slot = (await publish(trainerAccount, trainer.id, 72)).body.data;
  const results = await Promise.all([member, other].map((account) => api<{ data: Booking }>("/api/bookings", { method: "POST", cookie: account.cookie, body: { slotId: slot.id } })));
  assert.deepEqual(results.map((result) => result.response.status).sort(), [201, 409]);
  const winner = results.find((result) => result.response.status === 201)!;
  const owner = winner.body.data.memberId === member.id ? member : other;
  const retry = await api<{ data: Booking }>("/api/bookings", { method: "POST", cookie: owner.cookie, body: { slotId: slot.id } });
  assert.equal(retry.response.status, 200); assert.equal(retry.body.data.id, winner.body.data.id);
  const availability = await api<{ data: Slot[] }>(`/api/trainers/${trainer.id}/availability`);
  assert.equal(availability.body.data.some((item) => item.id === slot.id), false);
  assert.equal((await pool.query("SELECT count(*) FROM bookings WHERE slot_id = $1 AND status = 'confirmed'", [slot.id])).rows[0].count, "1");
});
test("a member cannot book overlapping sessions across two trainers, even concurrently", async () => {
  const first = (await publish(trainerAccount, trainer.id, 96)).body.data;
  const second = (await publish(secondTrainerAccount, secondTrainer.id, 96)).body.data;
  const results = await Promise.all([first, second].map((slot) => api("/api/bookings", { method: "POST", cookie: member.cookie, body: { slotId: slot.id } })));
  assert.deepEqual(results.map((result) => result.response.status).sort(), [201, 409]);
});
test("booking visibility is scoped to the member, assigned trainer or administrator", async () => {
  const slot = (await publish(trainerAccount, trainer.id, 120)).body.data;
  const booked = await api<{ data: Booking }>("/api/bookings", { method: "POST", cookie: member.cookie, body: { slotId: slot.id } });
  for (const [account, expected] of [[member, true], [other, false], [trainerAccount, true], [secondTrainerAccount, false], [admin, true]] as const) {
    const listing = await api<{ data: { bookings: Booking[] } }>("/api/bookings", { cookie: account.cookie });
    assert.equal(listing.body.data.bookings.some((item) => item.id === booked.body.data.id), expected);
  }
});
test("only owners can cancel, cancellation is repeat-safe and the slot becomes bookable", async () => {
  const slot = (await publish(trainerAccount, trainer.id, 144)).body.data;
  const booked = (await api<{ data: Booking }>("/api/bookings", { method: "POST", cookie: member.cookie, body: { slotId: slot.id } })).body.data;
  const cancelUrl = `/api/bookings/${booked.id}/cancel`;
  assert.equal((await api(cancelUrl, { method: "POST", cookie: other.cookie })).response.status, 404);
  assert.equal((await api(cancelUrl, { method: "POST", cookie: secondTrainerAccount.cookie })).response.status, 404);
  assert.equal((await api(`/api/trainers/${trainer.id}/availability/${slot.id}`, { method: "DELETE", cookie: trainerAccount.cookie })).response.status, 409);
  for (let repeat = 0; repeat < 2; repeat++) assert.equal((await api(cancelUrl, { method: "POST", cookie: member.cookie })).response.status, 200);
  assert.equal((await api("/api/bookings", { method: "POST", cookie: other.cookie, body: { slotId: slot.id } })).response.status, 201);
});
test("withdrawn slots disappear and cannot be booked", async () => {
  const slot = (await publish(trainerAccount, trainer.id, 168)).body.data;
  assert.equal((await api(`/api/trainers/${trainer.id}/availability/${slot.id}`, { method: "DELETE", cookie: trainerAccount.cookie })).response.status, 200);
  assert.equal((await api("/api/bookings", { method: "POST", cookie: member.cookie, body: { slotId: slot.id } })).response.status, 404);
});
test("database rejects forged booking times, cancelled-slot inserts and slot schedule edits", async () => {
  const slot = (await publish(trainerAccount, trainer.id, 192)).body.data;
  await assert.rejects(pool.query("INSERT INTO bookings(member_id, slot_id, trainer_id, starts_at, ends_at) VALUES ($1, $2, $3, $4, $5)", [member.id, slot.id, trainer.id, new Date(Date.parse(slot.startsAt) + 1000), slot.endsAt]), { code: "23514" });
  await assert.rejects(pool.query("UPDATE trainer_slots SET starts_at = starts_at + interval '1 minute' WHERE id = $1", [slot.id]), { code: "23514" });
  await api(`/api/trainers/${trainer.id}/availability/${slot.id}`, { method: "DELETE", cookie: trainerAccount.cookie });
  await assert.rejects(pool.query("INSERT INTO bookings(member_id, slot_id, trainer_id, starts_at, ends_at) VALUES ($1, $2, $3, $4, $5)", [member.id, slot.id, trainer.id, slot.startsAt, slot.endsAt]), { code: "23514" });
});
test("password recovery changes the password, invalidates sessions and is single-use", async () => {
  const recovery = await api("/api/auth/request-password-reset", { method: "POST", body: { email: other.email, redirectTo: `${base}/account` } });
  assert.equal(recovery.response.status, 200);
  const redirect = await fetch(await mailLink(other.email, "Reset"), { redirect: "manual" });
  const token = new URL(redirect.headers.get("location")!).searchParams.get("token"); assert.ok(token);
  const newPassword = `${password}-updated`;
  assert.equal((await api("/api/auth/reset-password", { method: "POST", body: { token, newPassword } })).response.status, 200);
  assert.equal((await api("/api/me", { cookie: other.cookie })).response.status, 401);
  assert.equal((await api("/api/auth/reset-password", { method: "POST", body: { token, newPassword } })).response.status, 400);
  other.cookie = await signIn(other.email, newPassword);
});
test("sign-out invalidates the database session", async () => {
  assert.equal((await api("/api/auth/sign-out", { method: "POST", cookie: other.cookie, body: {} })).response.status, 200);
  assert.equal((await api("/api/me", { cookie: other.cookie })).response.status, 401);
});
