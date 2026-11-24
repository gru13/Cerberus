<!-- Generated from sources.yaml by api/scripts/learn_index.py. Do not edit by hand. -->
# Learning index: realtime

<a id="realtime.asyncio-future-timeouts"></a>
### Futures, cancellation and timeouts in asyncio

Stories: 8.4.2 | Phase: P1
Keywords: Future, set_exception, cancel, asyncio.timeout, wait_for, pending requests

A request map holds one Future per request id; the reader task resolves them.
On disconnect, call set_exception on each pending Future so no caller hangs.
Check cancelled() before set_result, or an InvalidStateError can occur.
asyncio.timeout bounds a block; wait_for bounds one awaitable and cancels it.

Sources:
- [asyncio Future](https://docs.python.org/3/library/asyncio-future.html) (primary): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24
- [Coroutines and Tasks (timeout, wait_for)](https://docs.python.org/3/library/asyncio-task.html): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24

<a id="realtime.asyncio-queue-bounded"></a>
### Bounded asyncio.Queue

Stories: 8.4.1 | Phase: P1
Keywords: maxsize, QueueFull, put_nowait, backpressure, slow consumer

With maxsize above zero, await put() waits until a slot is free.
put_nowait raises QueueFull instead, which lets the server detect a slow consumer.
On QueueFull, drop the client or force a resync so memory stays flat.

Sources:
- [asyncio Queues](https://docs.python.org/3/library/asyncio-queue.html) (primary): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24

<a id="realtime.asyncio-unix-connection"></a>
### asyncio.open_unix_connection

Stories: 8.4.2 | Phase: P1
Keywords: Unix socket, StreamReader, StreamWriter, limit, sun_path

The coroutine returns a (reader, writer) pair for a Unix domain socket.
The limit argument sets the reader buffer size; the default is 64 KiB.
It is available on Unix only.
Socket path length limits come from the OS, not asyncio (see unix(7)).

Sources:
- [asyncio Streams](https://docs.python.org/3/library/asyncio-stream.html) (primary): Python Software Foundation, Python 3.15.2 docs, checked 2026-11-24

<a id="realtime.asyncpg-add-listener"></a>
### asyncpg add_listener

Stories: 8.4.4 | Phase: P1
Keywords: asyncpg, add_listener, notification callback, pool

add_listener(channel, callback) registers a callback on one connection.
The callback gets connection, pid, channel and payload.
Releasing a connection to a pool removes its listeners, so use a dedicated connection.

Sources:
- [asyncpg API Reference (Connection.add_listener)](https://magicstack.github.io/asyncpg/current/api/index.html) (primary): MagicStack, asyncpg docs, changelog to 0.32.0, checked 2026-11-24

<a id="realtime.caddy-flush-interval"></a>
### Caddy reverse_proxy flush_interval

Stories: 8.4.3 | Phase: P1
Keywords: flush_interval, -1, buffering, stream_close_delay, stream_timeout

A negative flush_interval (usually -1) turns off response buffering.
Caddy then flushes after every write, which suits streaming and terminals.
The same page covers stream_timeout and stream_close_delay for config reloads.
The page does not describe flush_interval for WebSockets; test it.

Sources:
- [reverse_proxy (Caddyfile directive)](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy) (primary): Caddy, unversioned (current docs), checked 2026-11-24

<a id="realtime.origin-check-websocket"></a>
### Origin check on the WebSocket upgrade

Stories: 8.4.1, 8.1.5 | Phase: P0
Keywords: CSWSH, Origin header, cross-site WebSocket hijacking, 403, allowlist

Browsers send cookies on the upgrade, so any site can open a socket as the user.
The server must compare Origin to an explicit allowlist and refuse with 403.
Avoid wildcards and substring matching; compare whole origins.
Origin does not stop non-browser clients, so keep real auth as well.

Sources:
- [WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html) (primary): OWASP Cheat Sheet Series, unversioned (current), checked 2026-11-24
- [RFC 6455 section 10.2, Origin Considerations](https://www.rfc-editor.org/rfc/rfc6455.html#section-10.2): IETF, RFC 6455 (December 2011), checked 2026-11-24

<a id="realtime.pg-listen"></a>
### PostgreSQL LISTEN

Stories: 8.4.4 | Phase: P1
Keywords: LISTEN, UNLISTEN, session scope, channel

LISTEN registers the current session on a channel.
Registration ends with the session, so a new connection must listen again.
Events sent while no session listens are not kept; catch up by id.
LISTEN takes effect at commit of its transaction.

Sources:
- [LISTEN](https://www.postgresql.org/docs/current/sql-listen.html) (primary): PostgreSQL Global Development Group, PostgreSQL 19, checked 2026-11-24

<a id="realtime.pg-notify"></a>
### PostgreSQL NOTIFY

Stories: 8.4.4 | Phase: P1
Keywords: NOTIFY, pg_notify, payload limit, queue, commit delivery

Notifications deliver only at commit; a rollback discards them.
The payload must be under 8000 bytes by default; send an id and fetch the row.
The queue is shared and finite; a full queue makes NOTIFY commits fail.
Check pg_notification_queue_usage() to watch it.

Sources:
- [NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html) (primary): PostgreSQL Global Development Group, PostgreSQL 19, checked 2026-11-24

<a id="realtime.pg-terminate-backend"></a>
### pg_terminate_backend

Stories: 8.4.4 | Phase: P1
Keywords: pg_terminate_backend, pg_stat_activity, fault injection, pg_signal_backend

The function ends the session of a given backend pid.
It needs superuser or the pg_signal_backend role, or membership of the target role.
Use it in tests to kill the listener connection and check reconnect and catch-up.
An optional timeout waits until the process exits.

Sources:
- [System Administration Functions (pg_terminate_backend)](https://www.postgresql.org/docs/current/functions-admin.html) (primary): PostgreSQL Global Development Group, PostgreSQL 19, checked 2026-11-24

<a id="realtime.pg-transaction-visibility"></a>
### Commit order and transaction visibility in PostgreSQL

Stories: 8.4.1 | Phase: P1
Keywords: xid8, pg_current_xact_id, pg_snapshot_xmin, snapshot, safe horizon, MVCC

A row is visible only after its transaction commits, in any id order.
A reader that saw id N+1 can miss id N if N commits later.
pg_current_xact_id gives a 64-bit transaction id; xmin of a snapshot marks a safe horizon.
Read only events from transactions older than that horizon to avoid gaps.

Sources:
- [System Information Functions (pg_current_xact_id, snapshots)](https://www.postgresql.org/docs/current/functions-info.html) (primary): PostgreSQL Global Development Group, PostgreSQL 19, checked 2026-11-24
- [Concurrency Control (MVCC)](https://www.postgresql.org/docs/current/mvcc.html): PostgreSQL Global Development Group, PostgreSQL 19, checked 2026-11-24

<a id="realtime.starlette-websocket"></a>
### Starlette and FastAPI WebSocket endpoints

Stories: 8.4.1 | Phase: P1
Keywords: WebSocket, accept, WebSocketDisconnect, receive, send

The WebSocket class gives accept, send, receive and close for one connection.
A client close raises WebSocketDisconnect on receive, so catch it to clean up.
FastAPI re-exports the Starlette class and adds route decorators.
A per-process connection list does not scale across processes; a bus is needed.

Sources:
- [WebSockets - Starlette](https://starlette.dev/websockets/) (primary): Starlette, unversioned (current docs), checked 2026-11-24
- [WebSockets - FastAPI](https://fastapi.tiangolo.com/advanced/websockets/): FastAPI, unversioned (current docs), checked 2026-11-24

<a id="realtime.tcp-nodelay"></a>
### TCP_NODELAY

Stories: 8.4.3 | Phase: P1
Keywords: Nagle, TCP_NODELAY, latency, small writes

The option turns off Nagle's algorithm so small writes go out at once.
Interactive streams such as terminals need this for low keystroke latency.
Set it with setsockopt at the IPPROTO_TCP level.

Sources:
- [tcp(7)](https://man7.org/linux/man-pages/man7/tcp.7.html) (primary): Linux man-pages project, Linux man-pages 6.19 (2026-04-19), checked 2026-11-24

<a id="realtime.uuid-v7"></a>
### UUID version 7

Stories: 8.4.1 | Phase: P1
Keywords: UUIDv7, time-ordered id, monotonic, RFC 9562

UUIDv7 puts a 48-bit millisecond timestamp first, then random bits.
Ids sort by creation time, which helps index locality.
Creation order is not commit order, so do not use it alone for resume.
Same-millisecond ids need a counter or sub-millisecond bits for monotonic order.

Sources:
- [Universally Unique IDentifiers (UUIDs)](https://www.rfc-editor.org/rfc/rfc9562.html) (primary): IETF, RFC 9562 (May 2024), checked 2026-11-24

<a id="realtime.websocket-ping-pong"></a>
### WebSocket ping and pong control frames

Stories: 8.4.1 | Phase: P1
Keywords: heartbeat, ping, pong, half-open TCP, control frame

Ping and pong are control frames; a pong must echo the ping payload.
Either side may ping at any time to test that the peer is alive.
A missing pong within a deadline means a dead or half-open link; close it.
Browsers cannot send protocol pings, so an app-level message may be needed.

Sources:
- [The WebSocket Protocol (sections 5.5.2 and 5.5.3)](https://www.rfc-editor.org/rfc/rfc6455.html) (primary): IETF, RFC 6455 (December 2011), checked 2026-11-24
- [Writing WebSocket servers](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers): MDN Web Docs, unversioned (current), checked 2026-11-24
