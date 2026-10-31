## Current testing policy

- Do not write, add, restore, or expand unit tests or isolated component tests.
- Keep automated tests limited to end-to-end workflows through the real application, service, CLI, browser, or device. Do not relabel isolated function or module tests as integration or end-to-end tests.
- Use appropriate builds, type checking, linting, static analysis, and direct runtime checks for other verification. Preserve the fixtures, helpers, and dependencies required by retained end-to-end tests.
- This owner policy supersedes older testing instructions below unless the owner explicitly changes it.

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
