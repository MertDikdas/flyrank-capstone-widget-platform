# Embeddable Widget & Lead-Capture Platform — Design

## 1. Problem

Website owners often need simple signup or contact widgets that can be embedded into websites they do not directly control.

This platform allows an authenticated customer to create a widget and receive a single embeddable `<script>` tag.

When a visitor submits the widget:

1. The request is validated.
2. Abuse and spam protections are applied.
3. The visitor IP is enriched with approximate geolocation.
4. The submission is stored.
5. A non-critical notification job is triggered.
6. The widget owner can view the lead through an authenticated dashboard API.

The public submission path must remain available even when optional services such as geolocation or email fail.


## 2. Core Actors

### Widget Owner

An authenticated customer who can:

- Create widgets
- Update widgets
- Delete widgets
- Retrieve embed snippets
- View submissions
- View basic analytics


### Customer Website

Any website that includes the generated widget script.

Example:

    <script src="http://localhost:8000/static/widget.v1.js?id=abc123"></script>


### Website Visitor

A public, unauthenticated user who:

- Sees the widget
- Fills the form
- Sends a submission to the public API


## 3. Data Model

### Tenant

Represents a customer account.

Fields:

- `id`
- `name`
- `created_at`


### User

Represents an authenticated platform user.

Fields:

- `id`
- `tenant_id`
- `email`
- `password_hash`
- `created_at`

Each user belongs to exactly one tenant.


### Widget

Represents an embeddable widget.

Fields:

- `id`
- `tenant_id`
- `name`
- `type`
- `title`
- `description`
- `button_text`
- `fields`
- `display_options`
- `is_active`
- `created_at`
- `updated_at`

Initial supported widget types:

- `CONTACT_FORM`
- `SIGNUP_FORM`

`fields` and `display_options` will be stored as JSONB.

Example field configuration:

    {
      "fields": [
        {
          "name": "email",
          "type": "email",
          "required": true
        },
        {
          "name": "message",
          "type": "text",
          "required": true
        }
      ]
    }

Every authenticated widget query must include the owner's `tenant_id`.


### Submission

Represents a visitor submission.

Fields:

- `id`
- `tenant_id`
- `widget_id`
- `payload`
- `idempotency_key`
- `ip_address`
- `country`
- `city`
- `created_at`

`payload` will be stored as JSONB.

Important indexes:

- `widget_id`
- `tenant_id`
- `created_at`
- `(widget_id, created_at)`

Unique constraint:

    (widget_id, idempotency_key)

This prevents the same retried submission from being stored more than once.


### NotificationJob

Represents a non-critical background side effect.

Fields:

- `id`
- `submission_id`
- `status`
- `attempt_count`
- `next_attempt_at`
- `last_error`
- `created_at`
- `completed_at`

Possible statuses:

    PENDING
    COMPLETED
    FAILED

The stored submission must never be rolled back because notification delivery failed.


## 4. Main Request Flows

### A. Widget Management

    Widget Owner
         |
         v
    Authenticated API
         |
         v
    Widget Service
         |
         v
    Widget Repository
         |
         v
    PostgreSQL

The authenticated tenant may only access its own widgets.


### B. Widget Loading

    Customer Website
         |
         v
    widget.v1.js
         |
         v
    GET /public/widgets/{id}/config
         |
         v
    Render Widget

The widget JavaScript is versioned and strongly cached.

Example JavaScript response:

    widget.v1.js

    Cache-Control: public, max-age=31536000, immutable

Widget configuration changes more frequently and therefore receives a shorter cache lifetime.

Example:

    Cache-Control: public, max-age=60


### C. Public Submission

    Website Visitor
         |
         v
    POST /public/widgets/{id}/submissions
         |
         v
    Boundary Validation
         |
         v
    Rate Limiting
         |
         v
    Spam Detection
         |
         v
    Geo Provider A
         |
       failure
         |
         v
    Geo Provider B
         |
       failure
         |
         v
    Continue Without Geo
         |
         v
    Store Submission
         |
         v
    Create Notification Job
         |
         v
    Return Success

Failure of geolocation or notification delivery must never destroy a valid submission.


## 5. API Surface

### Authentication

    POST /api/auth/register
    POST /api/auth/login


### Widget Management

Protected endpoints:

    POST   /api/widgets
    GET    /api/widgets
    GET    /api/widgets/{widget_id}
    PATCH  /api/widgets/{widget_id}
    DELETE /api/widgets/{widget_id}

All widget operations are tenant-isolated.


### Embed Snippet

    GET /api/widgets/{widget_id}/embed

Example response:

    {
      "snippet": "<script src=\"http://localhost:8000/static/widget.v1.js?id=abc123\"></script>"
    }


### Public Widget Configuration

    GET /public/widgets/{widget_id}/config

Authentication is not required.

The response only contains the data required by the browser to render the widget.


### Public Submission

    POST /public/widgets/{widget_id}/submissions

Authentication is not required.

Expected responses:

    201 Created
    400 Bad Request
    404 Not Found
    413 Payload Too Large
    422 Validation Error
    429 Too Many Requests

Malformed or invalid user input must never cause an unexpected `500 Internal Server Error`.


### Dashboard

Protected endpoints:

    GET /api/dashboard/submissions
    GET /api/dashboard/submissions/{submission_id}
    GET /api/dashboard/stats

Supported filters may include:

- `widget_id`
- `from`
- `to`
- `country`

Example statistics response:

    {
      "total_submissions": 128,
      "last_7_days": 34,
      "per_widget": {
        "contact-form": 90,
        "newsletter": 38
      },
      "countries": {
        "TR": 61,
        "DE": 27,
        "US": 15
      }
    }


## 6. Security and Abuse Protection

### Authentication

Administrative endpoints use bearer-token authentication.

Public widget endpoints do not require authentication.


### Tenant Isolation

Tenant ownership is enforced in backend database queries, not only in the frontend.

A widget lookup must follow the equivalent rule:

    WHERE widget.id = :widget_id
    AND widget.tenant_id = :current_tenant

Tenant A must never be able to read or modify Tenant B's widgets or submissions.


### CORS

The widget configuration and submission APIs are intentionally callable from websites hosted on different origins.

Public endpoints therefore support cross-origin requests and `OPTIONS` preflight requests.

Authentication cookies will not be used on public widget endpoints.


### Rate Limiting

Rate limits will be applied:

- Per IP address
- Per widget

When the limit is exceeded, the API returns:

    429 Too Many Requests

Rate limiting must prevent abusive traffic without making the entire API unavailable to legitimate users.


### Spam Protection

The first spam-protection mechanism will be a honeypot field.

Normal users never fill this hidden field.

If the honeypot contains a value:

    submission -> rejected or silently discarded


## 7. Geolocation Fallback

Provider order:

    ip-api.com
         |
       failure
         |
         v
    ipapi.co
         |
       failure
         |
         v
    Store without geo data

Geolocation is optional enrichment.

A valid lead must still be stored if both providers are unavailable.


## 8. Background Work

Notification delivery is performed outside the main submission request path.

Flow:

    Submission Stored
         |
         v
    NotificationJob Created
         |
         v
    Background Worker
         |
         v
    Attempt Delivery
       /       \
    Success   Failure
      |          |
      v          v
    COMPLETED   Retry
                  |
                  v
             Max Retries
                  |
                  v
                FAILED

Errors are stored in `last_error`.

A failed notification must never cause the original submission to disappear or return an error to the visitor after the submission has already been accepted.


## 9. Layered Architecture

The backend follows this structure:

    HTTP / API Layer
           |
           v
      Service Layer
           |
           v
    Repository Layer
           |
           v
       PostgreSQL


### API Layer Responsibilities

- HTTP request parsing
- Authentication
- Request validation
- HTTP response generation
- Correct HTTP status codes


### Service Layer Responsibilities

- Business rules
- Spam decisions
- Submission workflow
- Geolocation fallback
- Notification-job creation
- Tenant-aware business logic


### Repository Layer Responsibilities

- Database access
- Queries
- Persistence
- Tenant-aware data filtering


External integrations are isolated behind interfaces.

Geo providers:

    GeoProvider
      |
      +-- IpApiProvider
      |
      +-- IpApiCoProvider

Notification providers:

    NotificationProvider
      |
      +-- EmailNotificationProvider


## 10. Caching Strategy

The widget JavaScript bundle changes only when a new application version is released.

For that reason, it will use a versioned filename such as:

    widget.v1.js

with a long cache lifetime:

    Cache-Control: public, max-age=31536000, immutable

Widget configuration may change when its owner edits the widget, so configuration responses use a much shorter cache duration:

    Cache-Control: public, max-age=60

This allows fast widget loading without serving outdated configuration for long periods.


## 11. Idempotency

Public submission requests may be retried because of browser or network failures.

The client sends an idempotency key with each submission.

The database enforces uniqueness using:

    UNIQUE(widget_id, idempotency_key)

If the same request is retried, the system will not create a second lead.


## 12. Failure Philosophy

The public submission flow separates critical work from optional work.

Critical:

- Validate submission
- Protect against abuse
- Store submission

Non-critical:

- Geolocation enrichment
- Confirmation email
- Webhook notification

A failure in a non-critical dependency must degrade functionality instead of failing the submission.

Examples:

    Geo provider A fails
    -> try provider B

    Geo provider A and B fail
    -> store without geo

    Notification fails
    -> submission remains stored
    -> retry notification separately


## 13. Initial Technology Choices

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

Database:

- PostgreSQL

Infrastructure:

- Docker
- Docker Compose

External HTTP calls:

- httpx

Rate limiting:

- SlowAPI

Geo enrichment:

- ip-api.com
- ipapi.co

Email / notification testing:

- Mailpit or local console logging

Widget client:

- Vanilla JavaScript

Customer test website:

- Plain HTML served from a separate local origin


## 14. Local Development Origins

The API may run at:

    http://localhost:8000

The customer test website may run at:

    http://localhost:5500

Because the ports are different, these are different origins.

This allows real browser CORS and preflight behaviour to be tested locally.


## 15. Explicit Non-Goal

This project is not intended to become a complete form-builder or marketing automation platform.

The capstone will not include:

- Drag-and-drop form building
- Advanced visual customization
- Custom domains
- A real CDN
- Complex frontend dashboards
- Marketing automation workflows
- Large numbers of widget types

The widget UI will intentionally remain minimal.

The engineering focus is:

- Public API reliability
- Boundary validation
- CORS
- Rate limiting
- Spam protection
- Tenant isolation
- HTTP caching
- Background work
- Idempotency
- Graceful degradation