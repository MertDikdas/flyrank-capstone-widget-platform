# Build Log

## Phase 1 — Initial Design

### AI Usage

AI was used to help structure the initial system design, including the data model, API surface, request flows, and layered architecture.

I reviewed the proposed design and kept the parts that matched the capstone requirements. I also chose to include submission idempotency and a notification job early so that the shared capstone requirements for idempotency and background work are addressed naturally by the system design.

## Authentication and Persistence

Implemented PostgreSQL persistence with Alembic migrations.

Added tenant-aware user accounts, registration, login, JWT authentication, and a protected `/api/auth/me` endpoint.

Password hashing initially used Passlib with bcrypt, but the dependency combination failed under the current Python environment. It was replaced with pwdlib using Argon2 password hashing.