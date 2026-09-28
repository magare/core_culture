# Core Culture backend

Next.js App Router + TypeScript + PostgreSQL, with Drizzle migrations and Better Auth. This is a working first backend, not a production deployment. The static marketing website in `../site/` is preserved and is **not yet connected to these APIs**.

## Included

- Email/password registration, mandatory email verification, login/logout, seven-day database-backed sessions, and password recovery that revokes existing sessions.
- Member, trainer and administrator roles. Public registration always creates a member; role fields cannot be supplied by the client.
- Member phone/goal profile and preferred-trainer selection.
- Public trainer directory, specialty filter, individual profiles and available slots.
- Trainer-owned slot creation/withdrawal; administrator-only trainer provisioning.
- Booking and cancellation APIs with owner-scoped access and PostgreSQL concurrency protection.
- A small platform page and functional account-access page at `/account`. A full member booking interface and trainer/admin dashboards remain frontend work.
- Migrations, repeat-safe fictional seed data, validation tests and real HTTP/PostgreSQL integration tests.

## Run locally

Requirements: Node.js 22.12+ and a running local PostgreSQL 14+ instance. Use a currently supported PostgreSQL release for deployment. Migrations require permission to install the `btree_gist` extension.

From this repository:

```sh
cd backend
npm ci
npm run setup:local
npm run db:migrate
npm run db:seed
npm run dev
```

Open [the platform](http://127.0.0.1:3000), [account access](http://127.0.0.1:3000/account), or [health check](http://127.0.0.1:3000/api/health).

`setup:local` connects to local PostgreSQL using your operating-system username, creates **only** `core_culture_dev`, and creates a private `.env.local` with a random auth secret. It never overwrites an existing configuration or adopts an existing database automatically. If your local server needs different credentials, supply `LOCAL_POSTGRES_URL` securely in your environment. Otherwise configure `.env.local` from `.env.example` yourself and skip this script. Do not run the local setup against a production database.

The seed creates three clearly labelled fictional trainers and seven upcoming slots each, at 10:00 Asia/Kolkata. It creates **no administrator or shared-password accounts**. Running it repeatedly does not duplicate active slots. The existing static preview can continue running independently.

### Try registration

1. Open `/account`, choose “Create an account” and register with a password of at least 12 characters.
2. With `MAIL_MODE=outbox`, find the verification message in `backend/.local/mail/*.json`. Open its link locally. This folder contains sensitive tokens: keep it private, never commit or serve it, and discard expired development messages when no longer needed.
3. Sign in. The page links to your authenticated profile and bookings APIs.
   The account page also offers “Resend verification email” and confirms a
   successful verification callback.
4. “Forgot your password?” produces another private outbox message. The recovery link returns to `/account` with a reset token. A successful reset removes the token from the URL and returns to sign-in; invalid or expired email links show a recovery message.

No real mail leaves the machine in outbox mode. On a public host, configuration rejects outbox mode and HTTP URLs; configure SMTP and HTTPS instead. SMTP delivery happens in Next.js `after()`, so mail does not delay the authentication response. Failed deliveries are logged without message contents; production should add alerting/retry infrastructure. Verification can be resent through `/api/auth/send-verification-email`.

### Create administrators and trainers

Register and verify a dedicated account, then deliberately grant administrator access:

```sh
npm run user:role -- your-verified-email@example.com admin
```

This is a privileged local operator command, not a public API. Do not grant administrative access to a member or trainer by default. To provision a real trainer, have them register/verify, then use an administrator session with `POST /api/admin/trainers`. It atomically creates the trainer profile and changes that account's role. Existing sessions read the role from the database, without a stale authorization cache.

## API contract

All application responses use `{ "data": ... }` or `{ "error": { "code", "message", "requestId" } }`. Validation errors also include field issues. Better Auth routes retain Better Auth's own response shape. Dates are ISO 8601 timestamps; input must include a timezone, and output is UTC. Pagination uses bounded `limit` and `offset`. Availability defaults to the next 14 days, supports `from`/`to` up to 31 days, and returns at most 200 slots.

Every mutation requires `Origin` equal to `BETTER_AUTH_URL`. Requests with bodies use `Content-Type: application/json`; JSON bodies are capped at 16 KB. Sessions use HTTP-only cookies, with Secure enabled on HTTPS and the auth library's SameSite/CSRF protections. No wildcard CORS is enabled. Serve the eventual frontend and API on the same origin; do not wire browser requests directly from a `file://` page.

| Method | Endpoint | Access / purpose |
| --- | --- | --- |
| GET | `/api/health` | Public database readiness; 503 on failure |
| POST | `/api/auth/sign-up/email` | Register: `name`, `email`, `password` |
| POST | `/api/auth/sign-in/email` | Sign in after verification |
| GET | `/api/auth/get-session` | Current session |
| POST | `/api/auth/sign-out` | Sign out; JSON `{}` |
| POST | `/api/auth/send-verification-email` | Resend: `email`, optional `callbackURL` |
| POST | `/api/auth/request-password-reset` | `email`, `redirectTo` |
| POST | `/api/auth/reset-password` | `token`, `newPassword` |
| GET | `/api/me` | Verified account + member profile |
| PATCH | `/api/me` | Member; optional `phone` (E.164), `goal` |
| PUT | `/api/me/trainer` | Member; `trainerId`, or `null` to clear |
| GET | `/api/trainers` | Public; `specialty`, `limit`, `offset` |
| GET | `/api/trainers/:id` | Public UUID lookup; no account email exposed |
| GET | `/api/trainers/:id/availability` | Public available slots; `from`, `to` |
| POST | `/api/trainers/:id/availability` | Owning trainer/admin; `startsAt`, `endsAt` |
| DELETE | `/api/trainers/:id/availability/:slotId` | Owning trainer/admin; withdraw an unbooked slot |
| POST | `/api/admin/trainers` | Admin; verified `userId`, `slug`, `headline`, `bio`, `specialties`, `yearsExperience` |
| GET | `/api/bookings` | Member's own / trainer's assigned / admin's all; paginated |
| POST | `/api/bookings` | Member; `slotId` only; server determines all identities/times |
| POST | `/api/bookings/:id/cancel` | Member owner, assigned trainer, or admin |

Goals: `strength`, `fitness`, `mobility`, `endurance`, `general`, or `null`. Phone can also be cleared with `null`. Unknown fields are rejected on application writes.

For example, from a same-origin frontend with an authenticated session:

```ts
await fetch('/api/me/trainer', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ trainerId }),
});

await fetch('/api/bookings', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ slotId }),
});
```

## Scheduling rules

- First version: one club, one-to-one sessions, explicit immutable slots. No group capacity, recurring availability, payments, membership entitlements, or waitlists yet.
- Trainers can publish 15–120 minute slots between five minutes and 90 days ahead.
- A preferred trainer is a saved preference, not an exclusive assignment. Members may book any available trainer.
- Booking requires a future active slot. Exact repeat submissions for the same member/active slot return the existing booking, not a duplicate.
- PostgreSQL row locks, a partial unique index, and GiST exclusion constraints prevent simultaneous trainer/member overlaps. Adjacent slots are allowed (`[start, end)`). These are enforced even when requests race.
- Custom triggers prevent forged booking times, changing slot/booking identities, reactivating historical records, and withdrawing booked slots.
- Cancellation is repeat-safe, preserves history, and frees the slot. For now it is allowed until the start time; agree on the club's cancellation policy before launch.
- A slot must be withdrawn and recreated to change its schedule. Cancel its existing booking first if necessary.

## Verify

```sh
npm run check               # ESLint, Next type generation, TypeScript, 8 unit tests
npm run test:integration    # Real Next server + scratch PostgreSQL database
npm run build
npm start
```

Integration tests require a local PostgreSQL role with `CREATEDB`. Each invocation creates an unpredictable `core_culture_test_<id>` database, runs migrations, starts a separate server on a free loopback port, and tests actual HTTP/cookies/mail/concurrency. Only that invocation's scratch database is dropped afterward. Development data is untouched. Test mail remains under `.local/core_culture_test_<id>/mail` for debugging and is never served. Tests use a separate `.next-test` build directory.

Schema changes: edit `src/db/schema.ts`, run `npm run db:generate`, review the generated SQL, and run `npm run db:migrate`. PostgreSQL exclusion constraints and immutable-record triggers are deliberately maintained in `drizzle/0001_scheduling_guards.sql`; do **not** replace migrations with `drizzle-kit push`, which does not represent those guards in TypeScript.

ESLint is pinned to the version compatible with Next's current React lint plugin. The legacy esbuild dependency used by Drizzle's development tooling has a narrowly scoped patched-version override; rerun migration generation/tests when changing it.

## Before public launch

- Configure a managed PostgreSQL database with TLS certificate validation, backups, restoration testing and connection pooling. Use separate migration and least-privilege runtime roles. Never expose database credentials through `NEXT_PUBLIC_*` variables.
- Supply a fresh high-entropy `BETTER_AUTH_SECRET`, the exact HTTPS `BETTER_AUTH_URL`, `MAIL_MODE=smtp`, a verified sender, and `SMTP_URL` through your host's secret manager.
- The reverse proxy must **overwrite** `TRUSTED_IP_HEADER` (`x-real-ip` by default), and the origin must not be publicly reachable around that proxy. Add gateway-level rate/size limits to public reads and authentication. Auth limits are database-backed; application writes are capped at 30/minute per account.
- Deploy with `npm run build` / `npm start`, not the development server. The supplied start command binds to loopback; put a trusted reverse proxy in front or configure the platform's binding explicitly.
- Connect the marketing/member frontend to these APIs; replace fictional trainer content, define membership/access/cancellation rules, and build member/trainer/admin booking screens.
- Add operational alerting, mail retries, audit events, database/auth retention jobs and a reviewed privacy/consent policy. Payments and paid membership enforcement are intentionally not implemented.

No deployment, external service account, payment integration or real outbound email has been configured by this implementation.
