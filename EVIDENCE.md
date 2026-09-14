## Tenant Isolation

Tenant A created a widget.

Tenant B authenticated successfully but could not access Tenant A's widget.

Expected behavior:

- Tenant B listing widgets returned only its own widgets.
- Tenant B requesting Tenant A's widget returned `404 Not Found`.
- Tenant B could not update or delete Tenant A's widget.

This proves tenant ownership is enforced in backend queries rather than only in the client.