<!-- Generated from sources.yaml by api/scripts/learn_index.py. Do not edit by hand. -->
# Learning index: security

<a id="security.alembic-migrations"></a>
### Alembic migrations

Stories: 8.2.2 | Phase: P0
Keywords: alembic, revision, alembic_version, migration

Alembic runs versioned revision scripts against the database.
It keeps its own alembic_version table, which has no org_id.
Keep that table on the allow-list in the schema test.
Migrations also create the RLS policies and roles.

Sources:
- [Tutorial - Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) (primary): SQLAlchemy project (Alembic), Alembic 1.20.1, checked 2026-11-24

<a id="security.asgi-middleware"></a>
### Pure ASGI middleware and scope types

Stories: 8.1.5 | Phase: P0
Keywords: asgi, scope type, websocket scope, middleware

A pure ASGI middleware sees http and websocket scopes in one place.
Check scope["type"] to run logic for one kind only.
This lets one Origin or CSRF check cover WebSocket handshakes.
The guide notes CORSMiddleware does not block these.

Sources:
- [Middleware - Starlette](https://starlette.dev/middleware/) (primary): Starlette project, version not shown (current docs), checked 2026-11-24

<a id="security.constant-time-compare"></a>
### Constant-time comparison

Stories: 8.7.4, 4.3.3 | Phase: P1
Keywords: compare_digest, timing attack, constant time

Plain == can leak how many leading bytes match.
hmac.compare_digest compares in a way meant to resist timing attacks.
Use it to check signatures and token hashes.
The secrets module re-exports the same function.

Sources:
- [hmac - Keyed-Hashing for Message Authentication](https://docs.python.org/3/library/hmac.html) (primary): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24
- [secrets - Generate secure random numbers](https://docs.python.org/3/library/secrets.html): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24

<a id="security.csrf-defenses"></a>
### CSRF defenses

Stories: 8.1.5 | Phase: P0
Keywords: csrf, double-submit cookie, synchronizer token, origin check

Cookie-authenticated writes need a CSRF defense even with SameSite set.
The sheet prefers Sec-Fetch-Site first, with an Origin check as fallback.
It prefers signed double-submit over the naive form.
A missing or null Origin must not count as same-origin.

Sources:
- [Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) (primary): OWASP Cheat Sheet Series, undated (current), checked 2026-11-24

<a id="security.cswsh"></a>
### Cross-site WebSocket hijacking

Stories: 8.1.5, 8.4.1 | Phase: P0
Keywords: cswsh, websocket origin, handshake

Browsers attach cookies to WebSocket handshakes from any site.
A hostile page can then open an authenticated socket.
The server must validate Origin on every handshake and reject with 403.
RFC 6455 says a server that skips the check accepts all origins.

Sources:
- [WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html) (primary): OWASP Cheat Sheet Series, undated (current), checked 2026-11-24
- [RFC 6455: The WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455): IETF, RFC 6455 (Dec 2011), checked 2026-11-24

<a id="security.dns-rebinding"></a>
### DNS rebinding and Host allow-list

Stories: 8.1.5 | Phase: P0
Keywords: dns rebinding, host header, loopback

A hostile site can re-point its DNS name at 127.0.0.1 and then call a local API from the browser.
Domain checks done once at lookup time do not stop this.
The fix is to validate the Host header on every request against a fixed list.
The SSRF sheet states the limit of name-only allow-lists.

Sources:
- [Server-Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) (primary): OWASP Cheat Sheet Series, undated (current), checked 2026-11-24
- [Middleware - Starlette (TrustedHostMiddleware)](https://starlette.dev/middleware/): Starlette project, version not shown (current docs), checked 2026-11-24

<a id="security.docker-engine-api-create"></a>
### Docker Engine API container create

Stories: 8.10.2 | Phase: P0
Keywords: containers/create, hostconfig, api version prefix

The create call takes a HostConfig body with the risky fields.
The spec defines Privileged, Binds, CapAdd, NetworkMode and PidMode.
A body-checking proxy must read these fields.
Paths carry a version prefix such as /v1.47/.

Sources:
- [Docker Engine API v1.47 OpenAPI spec](https://docs.docker.com/reference/api/engine/version/v1.47.yaml) (primary): Docker Inc., API 1.47, checked 2026-11-24
- [Docker Engine API v1.47 reference](https://docs.docker.com/reference/api/engine/version/v1.47/): Docker Inc., API 1.47, checked 2026-11-24

<a id="security.docker-image-inspect"></a>
### docker image inspect

Stories: 2.2.3, 8.10.4 | Phase: P0
Keywords: image inspect, format, image size

The command prints detailed JSON for one or more images.
Use --format with a Go template to pick fields.
The page does not name a Size field; check the output yourself.
Use it for the image size limit.

Sources:
- [docker image inspect](https://docs.docker.com/reference/cli/docker/image/inspect/) (primary): Docker Inc., current (undated), checked 2026-11-24

<a id="security.docker-privileged-binds"></a>
### Privileged containers and host binds

Stories: 8.10.2 | Phase: P0
Keywords: privileged, binds, host mount, capabilities

Mounting the host root into a container lets it change the host filesystem freely.
Privileged adds all kernel capabilities.
Validate every create request if an API makes containers.
Drop all capabilities and add back only needed ones.

Sources:
- [Docker Engine security](https://docs.docker.com/engine/security/) (primary): Docker Inc., current (undated), checked 2026-11-24
- [Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html): OWASP Cheat Sheet Series, undated (current), checked 2026-11-24

<a id="security.docker-socket-proxy"></a>
### Docker socket proxy

Stories: 8.10.2 | Phase: P0
Keywords: docker.sock, socket proxy, haproxy, 403

The Tecnativa proxy exposes only chosen API sections through environment switches.
Blocked requests get 403.
It filters by section, not by request body.
The docker.sock grants root-equivalent control, per OWASP.

Sources:
- [Tecnativa/docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy) (primary): Tecnativa, no release listed; images :lts, :latest, :3.4; API 1.27-1.51, checked 2026-11-24
- [Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html): OWASP Cheat Sheet Series, undated (current), checked 2026-11-24

<a id="security.dockerfile-multistage-digest"></a>
### Multi-stage builds and digest pinning

Stories: 2.2.3 | Phase: P0
Keywords: multi-stage, digest pin, base image, final stage

Tags are mutable; a digest fixes the exact image.
Pinning stops automatic security fixes, so plan digest updates.
Multi-stage builds keep build tools out of the final image.
Check every FROM and the final USER.

Sources:
- [Building best practices](https://docs.docker.com/build/building/best-practices/) (primary): Docker Inc., current (undated), checked 2026-11-24
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/): Docker Inc., current (undated), checked 2026-11-24

<a id="security.dockerfile-parse"></a>
### dockerfile-parse library

Stories: 2.2.3 | Phase: P0
Keywords: dockerfile-parse, dockerfile ast, python

A Python library that parses Dockerfile files into instructions.
Use it to walk each FROM, ARG, ENV and USER.
The page shows no release number; pin the PyPI version yourself.
Hadolint is an optional extra linter.

Sources:
- [containerbuildsystem/dockerfile-parse](https://github.com/containerbuildsystem/dockerfile-parse) (primary): containerbuildsystem, no release listed on repo page, checked 2026-11-24

<a id="security.dockerfile-reference"></a>
### Dockerfile reference

Stories: 2.2.3 | Phase: P0
Keywords: from, arg, user, add, env

The reference defines every instruction the validator must parse.
FROM can use ARG values and names stages.
USER sets the default user for later steps and runtime.
ADD accepts URLs, and ENV values persist in the image.

Sources:
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) (primary): Docker Inc., current (undated), checked 2026-11-24

<a id="security.dockerignore"></a>
### dockerignore

Stories: 2.2.3 | Phase: P0
Keywords: dockerignore, build context, .git

The file sits in the build context root.
Matching paths are removed before the context goes to the builder.
Syntax is glob-like, with ! for exceptions; the last match wins.
A rule should exclude .git.

Sources:
- [Build context (.dockerignore)](https://docs.docker.com/build/concepts/context/) (primary): Docker Inc., current (undated), checked 2026-11-24

<a id="security.hadolint"></a>
### Hadolint

Stories: 2.2.3 | Phase: P0
Keywords: hadolint, dockerfile linter, shellcheck

Hadolint lints Dockerfiles against best practices.
It also checks shell code inside RUN steps.
Use it as an extra linter beside the custom rules.
It is written in Haskell and runs as a binary or container.

Sources:
- [hadolint/hadolint](https://github.com/hadolint/hadolint) (primary): Hadolint project, no release listed on repo page, checked 2026-11-24

<a id="security.hmac-signed-tokens"></a>
### HMAC-signed tokens

Stories: 8.7.4, 4.3.3 | Phase: P1
Keywords: hmac, signed token, expiry, single use

HMAC binds a message to a secret key, so the server can verify its own tokens.
Put run id, user id and expiry in the signed message.
Pair with a jti and an atomic consume for single use.
Use a digest name explicitly; digestmod is required.

Sources:
- [hmac - Keyed-Hashing for Message Authentication](https://docs.python.org/3/library/hmac.html) (primary): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104): IETF, RFC 2104 (Feb 1997), checked 2026-11-24

<a id="security.hyper-unix-socket"></a>
### hyper over a Unix socket

Stories: 8.10.2 | Phase: P0
Keywords: hyperlocal, hyper-util, unix domain socket

hyperlocal links hyper to Unix domain sockets for clients and servers.
hyper-util holds helper pieces and is less stable than hyper.
This is the base for a Rust proxy to the Docker socket.
Check crate versions against your hyper major version.

Sources:
- [hyperlocal](https://docs.rs/hyperlocal/latest/hyperlocal/) (primary): docs.rs (hyperlocal crate), hyperlocal 0.9.1, checked 2026-11-24
- [hyper-util](https://docs.rs/hyper-util/latest/hyper_util/): docs.rs (hyper-util crate), hyper-util 0.1.21, checked 2026-11-24

<a id="security.jwt-jti"></a>
### JWT ID (jti) claim

Stories: 8.7.4 | Phase: P1
Keywords: jti, replay, jwt, registered claim

jti is an optional registered claim that gives a token a unique id.
It can help stop a token from being replayed.
Store used jti values and consume each one once.
Ids must make accidental duplicates extremely unlikely.

Sources:
- [RFC 7519: JSON Web Token (JWT)](https://www.rfc-editor.org/rfc/rfc7519) (primary): IETF, RFC 7519 (May 2015), checked 2026-11-24

<a id="security.postgres-rls"></a>
### PostgreSQL row-level security

Stories: 8.2.2 | Phase: P0
Keywords: rls, force row level security, policy, table owner

Policies filter rows per role, as a second layer under app filters.
Table owners bypass policies unless FORCE ROW LEVEL SECURITY is set.
Use an app role that is not the owner.
A per-transaction setting can carry the org id.

Sources:
- [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) (primary): PostgreSQL Global Development Group, PostgreSQL 19 (current), checked 2026-11-24

<a id="security.python-contextvars"></a>
### contextvars and asyncio

Stories: 8.2.2 | Phase: P0
Keywords: contextvar, copy_context, asyncio task, tenant context

ContextVar holds per-request state such as the current tenant.
asyncio supports it natively; tasks copy the context when created.
A background job has no request context, so set it explicitly.
Fail closed when the variable is unset.

Sources:
- [contextvars - Context Variables](https://docs.python.org/3/library/contextvars.html) (primary): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24

<a id="security.python-secrets"></a>
### Python secrets module

Stories: 8.7.4 | Phase: P1
Keywords: secrets, token_urlsafe, csprng

secrets draws from the OS source of randomness and suits tokens.
token_urlsafe(n) returns n random bytes in URL-safe base64.
Do not use the random module for tokens.
It also offers compare_digest.

Sources:
- [secrets - Generate secure random numbers](https://docs.python.org/3/library/secrets.html) (primary): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24

<a id="security.samesite-cookies"></a>
### SameSite cookies and site vs origin

Stories: 8.1.5 | Phase: P0
Keywords: samesite, strict, site vs origin, localhost

Strict sends the cookie only on same-site requests; Lax also allows top-level safe navigations.
Site means scheme plus registrable domain; ports and subdomains do not change it.
Origin also needs host and port to match.
So preview subdomains can be same-site with the app, which needs a test.

Sources:
- [Set-Cookie header (SameSite)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) (primary): MDN Web Docs, current (undated), checked 2026-11-24
- [RFC 6454: The Web Origin Concept](https://www.rfc-editor.org/rfc/rfc6454): IETF, RFC 6454 (Dec 2011), checked 2026-11-24

<a id="security.sec-fetch-site"></a>
### Sec-Fetch-Site fetch metadata

Stories: 8.1.5 | Phase: P0
Keywords: sec-fetch-site, fetch metadata, same-site

The browser adds this request header with one of four values.
The values are cross-site, same-site, same-origin and none.
A server can reject writes that are not same-origin.
Older browsers omit it, so keep an Origin fallback.

Sources:
- [Sec-Fetch-Site header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Site) (primary): MDN Web Docs, current (undated), checked 2026-11-24
- [Fetch Metadata Request Headers](https://www.w3.org/TR/fetch-metadata/): W3C, Working Draft, 21 September 2026, checked 2026-11-24

<a id="security.secret-scanning-tools"></a>
### Secret scanning tools

Stories: 2.2.3 | Phase: P0
Keywords: gitleaks, detect-secrets, secret scan

Gitleaks scans repos, files and stdin for keys and tokens.
detect-secrets uses a baseline of known findings and blocks new ones.
Scan project files and image layers.
The gitleaks README says future releases are security patches only.

Sources:
- [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) (primary): Gitleaks project, no release listed on repo page, checked 2026-11-24
- [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets): Yelp, pre-commit example v1.5.0; releases not listed, checked 2026-11-24

<a id="security.sqlalchemy-loader-criteria"></a>
### with_loader_criteria

Stories: 8.2.2 | Phase: P0
Keywords: with_loader_criteria, global filter, relationship loading

It adds a filter for one entity everywhere it appears in a statement.
This includes joins, subqueries and relationship loads.
Use it inside do_orm_execute to scope by org_id.
Identity-map hits from session.get can bypass it.

Sources:
- [ORM API Features for Querying: with_loader_criteria](https://docs.sqlalchemy.org/en/20/orm/queryguide/api.html#sqlalchemy.orm.with_loader_criteria) (primary): SQLAlchemy project, SQLAlchemy 2.0.58, checked 2026-11-24

<a id="security.sqlalchemy-orm-execute-hook"></a>
### SQLAlchemy do_orm_execute hook

Stories: 8.2.2 | Phase: P0
Keywords: do_orm_execute, session events, tenant filter

This session event runs for ORM statements sent through Session.execute.
A handler can add criteria to every statement.
It does not see raw Core text() SQL sent outside the ORM path.
Combine it with with_loader_criteria.

Sources:
- [ORM Events: SessionEvents.do_orm_execute](https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.SessionEvents.do_orm_execute) (primary): SQLAlchemy project, SQLAlchemy 2.0.58, checked 2026-11-24

<a id="security.starlette-trustedhost"></a>
### Starlette TrustedHostMiddleware

Stories: 8.1.5 | Phase: P0
Keywords: trustedhostmiddleware, allowed_hosts, host header

The middleware checks the Host header against allowed_hosts.
A failed check returns 400.
A wildcard entry allows every host, so avoid it.
IPv6 hosts use bracket notation.

Sources:
- [Middleware - Starlette](https://starlette.dev/middleware/) (primary): Starlette project, version not shown (current docs), checked 2026-11-24

<a id="security.token-hashing-at-rest"></a>
### Hashing tokens at rest

Stories: 8.7.4 | Phase: P1
Keywords: token hash, sha-256, lookup by hash, entropy

Random high-entropy tokens need only a fast hash such as SHA-256, not bcrypt.
Store the hash and look up by hash.
Never store the raw token next to its hash.
Hashing does not help if the token itself leaks.

Sources:
- [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) (primary): OWASP Cheat Sheet Series, undated (current), checked 2026-11-24
- [secrets - Generate secure random numbers](https://docs.python.org/3/library/secrets.html): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24
