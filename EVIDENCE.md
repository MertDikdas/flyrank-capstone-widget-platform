## Tenant Isolation

Tenant A created a widget.

Tenant B authenticated successfully but could not access Tenant A's widget.

Expected behavior:

- Tenant B listing widgets returned only its own widgets.
- Tenant B requesting Tenant A's widget returned `404 Not Found`.
- Tenant B could not update or delete Tenant A's widget.

This proves tenant ownership is enforced in backend queries rather than only in the client.

## Cross-Origin Public Submission

A plain HTML customer page was served from:

    http://localhost:5500

The API was served from:

    http://localhost:8000

The browser successfully completed the CORS preflight request and submitted a valid lead to the public submission endpoint.

Observed request flow:

    OPTIONS /public/widgets/{widget_id}/submissions
    POST /public/widgets/{widget_id}/submissions

The submission returned a successful 2xx response and the resulting row was verified in PostgreSQL.

## Cross-Origin Public Submission

A plain HTML customer page was served from:

    http://localhost:5500

The API was served from:

    http://localhost:8000

The browser successfully completed the CORS preflight request and submitted a valid lead to the public submission endpoint.

Observed request flow:

    OPTIONS /public/widgets/{widget_id}/submissions
    POST /public/widgets/{widget_id}/submissions

The submission returned a successful 2xx response and the resulting row was verified in PostgreSQL.

## Abuse Protection

### Rate Limiting

The public submission endpoint enforces request limits at the API boundary.

A burst of submissions from the same client produced successful responses until the configured limit was reached, after which the API returned:

    429 Too Many Requests

The service remained responsive after the rejected burst.

### Honeypot Spam Protection

The customer form contains a hidden honeypot field that normal visitors do not fill.

A submission with the honeypot populated was rejected with a 4xx response and was verified not to exist in PostgreSQL.

This demonstrates that obvious automated form-filling traffic is blocked before persistence.

## Geo Enrichment Fallback

The submission flow enriches visitor IP addresses with approximate location data.

### Provider A available

Configuration:

    GEO_PROVIDER_A_ENABLED=true
    GEO_PROVIDER_B_ENABLED=true

A valid submission was stored with:

    country = Turkey
    city = Izmir

### Provider A unavailable

Configuration:

    GEO_PROVIDER_A_ENABLED=false
    GEO_PROVIDER_B_ENABLED=true

The submission still succeeded and was enriched by the fallback provider:

    country = Germany
    city = Berlin

### All providers unavailable

Configuration:

    GEO_PROVIDER_A_ENABLED=false
    GEO_PROVIDER_B_ENABLED=false

The submission still returned a successful response and was stored.

The resulting database row contained:

    country = NULL
    city = NULL

This proves geolocation is optional enrichment and failure of all providers does not break the main submission path.

## Background Notification and Failure Isolation

A notification job is created after a valid submission is persisted.

Notification delivery runs asynchronously through a database-backed job processed by APScheduler.

With notification delivery working:

    status = COMPLETED

When notification delivery was deliberately forced to fail:

    NOTIFICATION_FORCE_FAIL=true

the public submission endpoint still returned a successful response and the submission remained stored in PostgreSQL.

The background job retried independently and eventually reached:

    status = FAILED
    attempt_count = 3
    last_error = Simulated notification failure

This demonstrates that failure of a non-critical side effect does not break the primary submission path.

## Owner Dashboard

Authenticated widget owners can retrieve their stored submissions and aggregated statistics.

Verified endpoints:

    GET /api/dashboard/submissions
    GET /api/dashboard/submissions/{submission_id}
    GET /api/dashboard/stats

The statistics endpoint reports:

- total submission count
- submissions from the last seven days
- counts grouped by widget
- counts grouped by country
- daily submission counts

Dashboard queries are tenant-isolated.

A second tenant could not list or retrieve submissions belonging to the first tenant, and direct access to another tenant's submission returned:


## Acceptance Probe 1 — Valid Public Submission

A valid submission was sent to the seeded demo widget.

Response:

    HTTP/1.1 201 Created

Returned submission:

    id = e6c2ba32-59ab-45fb-a8f6-378035151098
    widget_id = 33333333-3333-3333-3333-333333333333

The authenticated dashboard returned the same submission with:

    email = probe1@example.com
    message = Acceptance probe one

The submission was also verified directly in PostgreSQL.

Result: PASS


## Acceptance Probe 2 — Invalid and Oversized Payloads

Missing required `message` field:

    HTTP/1.1 422 Unprocessable Content

Response:

    {"detail":{"message":"Missing required fields","fields":["message"]}}

Oversized message (>5000 characters):

    HTTP/1.1 413 Content Too Large

Response:

    {"detail":"Field 'message' is too large"}

Neither invalid request produced an HTTP 500 response.

Result: PASS

## Acceptance Probe 3 — Rate Limiting and Recovery

A burst of eight submissions was sent from the same client.

Observed responses:

    request 1 -> 201
    request 2 -> 201
    request 3 -> 201
    request 4 -> 201
    request 5 -> 201
    request 6 -> 429
    request 7 -> 429
    request 8 -> 429

After waiting for the short rate-limit window to expire, a normal request succeeded:

    HTTP/1.1 201 Created

This proves burst traffic is rejected without leaving the service unavailable.

### Idempotency verification

The same request was sent twice with the same `Idempotency-Key`.

Both responses returned the same submission ID:

    edbd3f90-b5c1-411c-b34f-c4554bc9c0e5

No duplicate submission was created.

Result: PASS

## Acceptance Probe 4 — Geo Fallback and Graceful Degradation

### Provider A unavailable, Provider B available

Configuration:

    GEO_PROVIDER_A_ENABLED=false
    GEO_PROVIDER_B_ENABLED=true

A valid submission returned:

    HTTP 201 Created

The stored submission was enriched by Provider B:

    country = Germany
    city = Berlin

### All geo providers unavailable

Configuration:

    GEO_PROVIDER_A_ENABLED=false
    GEO_PROVIDER_B_ENABLED=false

A valid submission still returned:

    HTTP 201 Created

The submission was stored successfully with:

    country = NULL
    city = NULL

This proves that geolocation enrichment degrades gracefully and does not break the main submission path.

Result: PASS

## Acceptance Probe 5 — Notification Failure Isolation

Notification delivery was deliberately forced to fail:

    NOTIFICATION_FORCE_FAIL=true

A valid public submission still returned:

    HTTP 201 Created

The submission was verified in PostgreSQL.

The background notification job retried independently and eventually reached:

    status = FAILED
    attempt_count = 3
    last_error = Simulated notification failure

The failed side effect did not roll back or reject the stored submission.

Result: PASS

## Acceptance Probe 6 — Honeypot Spam Protection

A bot-like submission populated the hidden honeypot field.

The API returned:

    HTTP 400 Bad Request

Response:

    {"detail":"Invalid submission"}

A PostgreSQL query confirmed that no submission was stored for the spam payload.

Result: PASS