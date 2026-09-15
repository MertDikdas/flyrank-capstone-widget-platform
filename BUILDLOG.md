# Build Log

## Phase 1 — Initial Design

### AI Usage

AI was used to help structure the initial system design, including the data model, API surface, request flows, and layered architecture.

I reviewed the proposed design and kept the parts that matched the capstone requirements. I also chose to include submission idempotency and a notification job early so that the shared capstone requirements for idempotency and background work are addressed naturally by the system design.

## Authentication and Persistence

Implemented PostgreSQL persistence with Alembic migrations.

Added tenant-aware user accounts, registration, login, JWT authentication, and a protected `/api/auth/me` endpoint.

Password hashing initially used Passlib with bcrypt, but the dependency combination failed under the current Python environment. It was replaced with pwdlib using Argon2 password hashing.

## Public Submission Hardening

Added cross-origin submission support, request rate limiting, and honeypot-based spam protection.

CORS was tested from a separate local origin. I also verified that changing the allowed origin causes the browser to block access to the response even if the backend processed the request.

Rate limiting was tested with burst traffic and returned 429 responses after the configured threshold.

A honeypot field was added to reject simple automated form submissions before persistence. 

## Capstone Hardening and Acceptance Testing

Completed the full public submission pipeline and evaluated it against the published acceptance probes.

Implemented and verified:

- cross-origin widget submissions
- dynamic payload validation
- idempotent submission handling
- per-IP and per-widget rate limiting
- honeypot spam protection
- geolocation provider fallback
- graceful degradation when geo providers are unavailable
- durable background notification jobs
- retry and permanent failure handling
- cached widget delivery
- tenant-isolated dashboard analytics

During development, several implementation details were changed after testing:

- Passlib/bcrypt was replaced with pwdlib/Argon2 because the installed bcrypt version was incompatible with Passlib.
- CORS behavior was tested from a separate browser origin and clarified that CORS is enforced by the browser rather than acting as server-side authentication.
- The rate-limit window was adjusted during acceptance testing so burst rejection and subsequent service recovery could be demonstrated deterministically.
- The seed script was changed to run as a Python module so project-level imports resolve correctly.

All published acceptance probes were executed locally before submission.