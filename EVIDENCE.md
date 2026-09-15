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
