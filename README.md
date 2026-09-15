# Embeddable Widget & Lead-Capture Platform

Backend capstone project built for the FlyRank Backend Internship.

The platform allows an authenticated customer to create embeddable contact/signup widgets and install them on an external website using a single `<script>` tag.

Visitor submissions are accepted through a hardened public API with validation, tenant isolation, idempotency, rate limiting, spam protection, geolocation enrichment, fallback handling, background notification jobs, and dashboard analytics.

---

## Core Features

- Authenticated widget CRUD
- Multi-tenant data isolation
- JWT authentication
- Argon2 password hashing
- Single-line embeddable widget script
- Public widget configuration endpoint
- Cross-origin form submissions
- CORS and preflight support
- Dynamic payload validation
- Idempotent submissions
- Per-IP and per-widget rate limiting
- Honeypot spam protection
- IP geolocation enrichment
- Geo provider fallback chain
- Graceful degradation when geo providers fail
- Database-backed background notification jobs
- Notification retries and permanent failure tracking
- Cached and versioned widget JavaScript
- Owner submission dashboard
- Aggregated dashboard statistics
- PostgreSQL persistence
- Alembic database migrations

---

## Architecture

```text
                     ┌─────────────────────────┐
                     │      Widget Owner       │
                     │     Authenticated       │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │ Widget Management API   │
                     │ Auth / CRUD / Dashboard │
                     └────────────┬────────────┘
                                  │
                                  ▼
                           ┌────────────┐
                           │ PostgreSQL │
                           └────────────┘


External Customer Website
http://localhost:5500

        │
        │ <script src="...widget.v1.js?id=...">
        ▼
┌─────────────────────────────┐
│       widget.v1.js          │
│ versioned + long-term cache │
└─────────────┬───────────────┘
              │
              │ GET widget config
              ▼
┌─────────────────────────────┐
│ Public Widget Config API    │
│ short-lived HTTP cache      │
└─────────────────────────────┘

Visitor submits form
        │
        ▼
┌─────────────────────────────┐
│ Public Submission Endpoint  │
└─────────────┬───────────────┘
              │
              ▼
       Rate Limiting
              │
              ▼
       Spam Protection
              │
              ▼
      Payload Validation
              │
              ▼
       Idempotency Check
              │
              ▼
       Geo Provider A
              │
           failure
              ▼
       Geo Provider B
              │
           failure
              ▼
       Continue Without Geo
              │
              ▼
         PostgreSQL
              │
              ▼
      Notification Job
              │
              ▼
      Background Worker
         /          \
    success        retry
      │              │
 COMPLETED         FAILED
```

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL
- Docker

### Security

- JWT
- Argon2 password hashing
- Boundary validation
- Tenant-aware queries
- Rate limiting
- Honeypot spam protection

### Background Processing

- APScheduler
- Database-backed notification jobs

### External Integrations

- `ip-api.com`
- `ipapi.co`
- `httpx`

Deterministic mock providers are used when proving fallback behaviour.

### Widget Client

- Vanilla JavaScript
- Plain HTML test website

---

# Local Setup

## Requirements

Install:

- Python 3
- Docker
- Docker Compose
- Git

---

## 1. Clone

```bash
git clone https://github.com/MertDikdas/flyrank-capstone-widget-platform.git
cd flyrank-capstone-widget-platform
```

---

## 2. Create the virtual environment

```bash
python3 -m venv .venv
```

Activate it:

macOS / Linux:

```bash
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## 4. Configure environment

```bash
cp .env.example .env
```

The default local configuration is sufficient for the demo.

No real credentials are committed to the repository.

---

# Run

Run the complete local environment with:

```bash
./scripts/run.sh
```

This command:

1. starts PostgreSQL with Docker
2. applies Alembic migrations
3. starts the second-origin customer test website
4. starts the FastAPI application

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Customer test website:

```text
http://localhost:5500
```

---

# Seed Demo Data

In another terminal:

```bash
.venv/bin/python -m scripts.seed
```

Demo credentials:

```text
Email:    demo@example.com
Password: DemoPassword123!
```

Demo widget:

```text
33333333-3333-3333-3333-333333333333
```

The customer test page is configured to load this widget.

---

# Main API Endpoints

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

---

## Widget Management

Authenticated:

```text
POST   /api/widgets
GET    /api/widgets
GET    /api/widgets/{widget_id}
PATCH  /api/widgets/{widget_id}
DELETE /api/widgets/{widget_id}
GET    /api/widgets/{widget_id}/embed
```

All database queries enforce tenant ownership.

---

## Public Widget Delivery

```text
GET /static/widget.v1.js

GET /public/widgets/{widget_id}/config
```

Widget JavaScript:

```text
Cache-Control: public, max-age=31536000, immutable
```

Widget configuration:

```text
Cache-Control: public, max-age=60
```

---

## Public Submission

```text
POST /public/widgets/{widget_id}/submissions
```

Required header:

```text
Idempotency-Key
```

Example body:

```json
{
  "payload": {
    "email": "visitor@example.com",
    "message": "Hello"
  },
  "honeypot": ""
}
```

Submission processing includes:

1. rate limiting
2. spam detection
3. dynamic field validation
4. idempotency handling
5. geolocation enrichment
6. persistence
7. asynchronous notification-job creation

---

## Dashboard

Authenticated:

```text
GET /api/dashboard/submissions
GET /api/dashboard/submissions/{submission_id}
GET /api/dashboard/stats
```

Supported submission filters include:

```text
widget_id
country
limit
offset
```

Statistics include:

- total submissions
- submissions in the last seven days
- submissions per widget
- country breakdown
- daily counts

---

# Tenant Isolation

Each user belongs to a tenant.

Widgets and submissions are associated with that tenant.

Authenticated resource queries include the tenant identifier:

```text
resource.tenant_id == current_user.tenant_id
```

A user requesting another tenant's resource receives `404 Not Found`.

Tenant isolation is enforced by the backend and database queries, not by the user interface.

---

# Submission Idempotency

Every submission carries an `Idempotency-Key`.

The database enforces:

```text
UNIQUE(widget_id, idempotency_key)
```

This prevents network retries from creating duplicate leads.

Application-level lookup improves the normal retry path while the database constraint provides the final concurrency guarantee.

---

# Graceful Degradation

Geolocation and notifications are non-critical side effects.

The submission itself is the critical operation.

Geo flow:

```text
Provider A
   ↓ failure
Provider B
   ↓ failure
Store without geo
```

A failure in all geolocation providers does not reject a valid lead.

Notification delivery occurs independently after persistence.

A failed notification:

- does not roll back the submission
- is retried
- records the last error
- eventually becomes `FAILED` after the retry limit

---

# Evidence

Behavioural proof for capstone requirements is recorded in:

```text
EVIDENCE.md
```

This includes evidence for:

- tenant isolation
- cross-origin submission
- validation
- idempotency
- rate limiting
- honeypot blocking
- geo fallback
- notification failure isolation
- dashboard isolation

---

# AI Usage

AI-assisted development is documented honestly in:

```text
BUILDLOG.md
```

The log records:

- where AI assisted
- implementation decisions reviewed by the developer
- incorrect suggestions or dependency issues
- changes made after testing

---

# Limitations

This capstone intentionally focuses on backend engineering rather than building a complete marketing platform.

Current limitations:

- The widget UI is intentionally minimal.
- No visual drag-and-drop form builder is included.
- No real CDN is used.
- The rate limiter uses local process state; a distributed deployment should use a shared store such as Redis.
- Notification delivery is demonstrated locally rather than through a production email provider.
- Geo fallback proof uses deterministic mock behaviour.
- The background scheduler runs inside the application process for this local capstone environment.
- Production hosting is outside the core capstone scope.
- Advanced bot detection such as CAPTCHA is not implemented.

---

# Project Documentation

- `DESIGN.md` — initial architecture and system design
- `EVIDENCE.md` — behavioural acceptance evidence
- `BUILDLOG.md` — development and AI-assistance log
- `capstone.yaml` — evaluator run manifest
- `.env.example` — safe environment-variable template

---

# Repository

FlyRank Backend Internship Capstone

Embeddable Widget & Lead-Capture Platform