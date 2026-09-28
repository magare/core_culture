# Site cleanup — 26 September 2026

The marketing preview was checked at `http://127.0.0.1:8931/site/` and the
separate account service at `http://127.0.0.1:3000/account`. Existing designs,
model exports, and unrelated working-tree edits were retained.

## Changes

- Removed page overflow caused by oversized mobile headings and the footer
  wordmark. Used readable condensed type for class names, times, equipment,
  space labels, and membership titles. Kept the established brand headlines.
- Kept navigation available while scrolling and improved mobile form spacing.
- Preserved the previous room when opening its equipment directory, and the
  previous section when starting a visit preview. Restored keyboard focus after
  browser history completes its own focus changes.
- Showed the next seven dates in the timetable, omitted finished sessions,
  added result counts and a useful empty-state action, and carried session
  dates/times into the visit form.
- Moved the preview explanation above the fields, made submission labels
  explicit, removed the artificial delay, rejected malformed plus signs in
  phone numbers, and cleared personal details after a successful preview.
- Added account verification resend, a verification callback message, recovery
  from invalid email links, readable network errors, duplicate-submit guards,
  and reset-token removal. Registration returns to sign-in with email retained.

## Verification

- 95 browser assertions passed for mobile navigation, desktop anchors, the
  space rail, all eight room dialogs/images, galleries, nested Escape behavior,
  focus restoration, Back/Forward, equipment search/filter/reset/specifications,
  schedule days/categories/events/keyboard tabs, enquiries, validation, and
  all three membership handoffs, and returning from an enquiry through its room.
- 20 browser assertions passed for 3D presets, labels, real camera changes,
  keyboard orbit/reset/Escape, one-canvas expanded view, mobile sizing, focus
  restoration, and blocked-download retry with cleanup of the failed canvas.
- No horizontal page overflow at 320, 360, 390, 768, 1024, 1200, 1440, or 1920 CSS
  pixels. The space rail intentionally scrolls horizontally within the page.
- 12 account browser checks passed with real local outbox mail: registration,
  unverified-account rejection, verification resend/callback, sign-in and
  session persistence, sign-out, recovery email, password reset, old-password
  rejection, expired links, network retry, and mobile layout. The fictional QA
  account and its mail were removed afterward. No real email was sent.
- Mobile room overflow and Tab/Shift+Tab wrapping were also checked.
- Backend lint, TypeScript checks, eight validation tests, and production build
  passed. All 22 HTTP/PostgreSQL integration tests passed, including concurrent
  booking protection, ownership checks, cancellation, verification, password
  reset, and sign-out. Integration tests used a disposable database.
- All 11 site smoke tests passed. Five of six model tests passed; the remaining
  check reports the pre-existing Blender source fingerprint mismatch described
  below. JavaScript syntax checks and whitespace checks passed.

Browser scripts and screenshots are in `output/playwright/`. Deliberately
blocked model/network requests generate expected browser errors during recovery
tests; they are not normal page-load failures.

## Boundaries

The marketing form remains an explicitly labelled local preview. It sends no
request and does not create a booking. Account and booking APIs are still a
separate application; no new member/trainer dashboard or deployment was added.

The model export records source SHA-256
`c449cda0b93c29af9584660bad64c2d0c8d0f8fc14bcb9d75dd112bfc6b33337`, while the
current Blender source hashes to
`51b521bb2ed6876096d2cab0f27e6a0fca9c33a2c7828767ccdbe74338e8cc08`.
This mismatch was present before the cleanup. Neither the source nor the
manifest was changed to conceal it. The exported GLB validates and renders;
re-exporting from the changed source is a separate model update.

Checks used Chromium. Physical touch devices, Safari, and Firefox were not
tested in this pass.
