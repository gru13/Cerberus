<!-- Generated from sources.yaml by api/scripts/learn_index.py. Do not edit by hand. -->
# Learning index: persistence

<a id="persistence.asyncio-tasks-timers"></a>
### asyncio tasks and timers

Stories: 8.8.2 | Phase: P1
Keywords: create_task, TaskGroup, timers, task reference

create_task schedules a coroutine as a Task.
Keep a reference to each task, or the loop may drop it early.
Cancel pending timers and tasks on shutdown.

Sources:
- [Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html) (primary): Python Software Foundation, Python 3.15.2, checked 2026-11-24

<a id="persistence.durable-write-fsync"></a>
### Durable writes: fsync and atomic rename

Stories: 8.8.1 | Phase: P1
Keywords: fsync, rename, durability, directory fsync

Write a temp file, fsync it, rename it, then fsync the directory.
fsync on a file does not make its directory entry durable.
rename replaces the target in one atomic step.
The save response waits until this sequence ends.

Sources:
- [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html) (primary): Linux man-pages project, Linux man-pages 6.19, checked 2026-11-24
- [rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html): Linux man-pages project, Linux man-pages 6.19, checked 2026-11-24

<a id="persistence.http-etag-if-match"></a>
### HTTP ETag and If-Match

Stories: 8.8.3 | Phase: P1
Keywords: ETag, If-Match, 412, 409, precondition

An ETag names one version of a resource.
If-Match makes a write apply only when the ETag still matches.
A failed precondition returns 412; this project plans 409 with server version.

Sources:
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) (primary): IETF, RFC 9110 (June 2022), checked 2026-11-24

<a id="persistence.optimistic-compare-and-swap"></a>
### Optimistic concurrency with compare-and-swap

Stories: 8.8.3 | Phase: P1
Keywords: compare-and-swap, base_hash, UPDATE WHERE, read committed

UPDATE ... WHERE hash = base changes the row only if no one else did.
Under Read Committed a waiting UPDATE re-checks its WHERE after the other commit.
Zero rows updated means a conflict.
Same new hash as the server has means replay, not conflict.

Sources:
- [Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html) (primary): PostgreSQL Global Development Group, PostgreSQL 19, checked 2026-11-24

<a id="persistence.pg-advisory-locks"></a>
### PostgreSQL advisory locks

Stories: 8.5.2, 8.8.4 | Phase: P1
Keywords: advisory lock, pg_advisory_xact_lock, mutual exclusion

Application-defined locks that the server does not enforce itself.
Session level locks last until release or disconnect.
Transaction level locks end at commit or rollback, which is safer.
Pick a stable key scheme, such as a hash of run id.

Sources:
- [Explicit Locking (advisory locks)](https://www.postgresql.org/docs/current/explicit-locking.html) (primary): PostgreSQL Global Development Group, PostgreSQL 19, checked 2026-11-24

<a id="persistence.problem-json"></a>
### Problem Details for HTTP APIs

Stories: 8.8.3 | Phase: P1
Keywords: application/problem+json, RFC 9457, error format

A standard JSON shape for API errors: type, title, status, detail, instance.
Extra members can carry data, such as the server version.
RFC 9457 replaces RFC 7807.

Sources:
- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html) (primary): IETF, RFC 9457 (July 2023), checked 2026-11-24

<a id="persistence.procrastinate-retry"></a>
### Procrastinate retry strategy

Stories: 8.5.2 | Phase: P1
Keywords: RetryStrategy, max attempts, backoff

A task can retry a set number of times or use a RetryStrategy object.
Custom retry logic can decide per exception.
Failed jobs can also be retried by hand.
Do not build a second lease system beside this one.

Sources:
- [Define a retry strategy on a task](https://procrastinate.readthedocs.io/en/stable/howto/advanced/retry.html) (primary): Procrastinate project, stable (no version number shown), checked 2026-11-24

<a id="persistence.python-hashlib"></a>
### Python hashlib

Stories: 8.8.1 | Phase: P1
Keywords: hashlib, sha256, file_digest

hashlib.sha256 gives a hash object with update and hexdigest.
file_digest hashes a binary file object (Python 3.11+).
Hash large files in chunks and use a thread for blocking I/O.

Sources:
- [hashlib - Secure hashes and message digests](https://docs.python.org/3/library/hashlib.html) (primary): Python Software Foundation, Python 3.15.2, checked 2026-11-24

<a id="persistence.sha256-content-addressing"></a>
### SHA-256 and content addressing

Stories: 8.8.1 | Phase: P1
Keywords: SHA-256, content addressing, dedupe, blob store

SHA-256 is a standard hash that gives a fixed-size digest.
The digest of the bytes names the blob, so equal files share one blob.
Same files give the same hash, which makes snapshots deterministic.
Hash the raw bytes, not decoded text.

Sources:
- [FIPS 180-4, Secure Hash Standard (SHS)](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) (primary): NIST, FIPS 180-4 (August 2015), checked 2026-11-24

<a id="persistence.skip-locked"></a>
### SELECT FOR UPDATE SKIP LOCKED

Stories: 8.5.2 | Phase: P1
Keywords: SKIP LOCKED, job queue, reaper

Rows that another transaction holds locked are skipped, not waited on.
Several workers can claim different rows without blocking each other.
The result is not a consistent view, so use it for queues only.
A reaper can use it to requeue expired leases safely.

Sources:
- [SELECT, locking clause](https://www.postgresql.org/docs/current/sql-select.html) (primary): PostgreSQL Global Development Group, PostgreSQL 19, checked 2026-11-24

<a id="persistence.sqlalchemy-async"></a>
### SQLAlchemy asyncio extension

Stories: 8.8.1, 8.8.3 | Phase: P1
Keywords: AsyncSession, create_async_engine, asyncpg

Core and ORM work through AsyncEngine and AsyncSession.
Lazy loading does not work in async code, so load data explicitly.
One AsyncSession must not be shared between concurrent tasks.

Sources:
- [Asynchronous I/O (asyncio)](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) (primary): SQLAlchemy project, SQLAlchemy 2.0.58, checked 2026-11-24

<a id="persistence.sqlalchemy-for-update"></a>
### SQLAlchemy with_for_update

Stories: 8.8.1, 8.8.3 | Phase: P1
Keywords: with_for_update, row lock, skip_locked

with_for_update adds FOR UPDATE to a SELECT.
Options such as of, nowait and skip_locked change the lock behavior.
Use it to serialize writers per (run, path) row.

Sources:
- [GenerativeSelect.with_for_update](https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.GenerativeSelect.with_for_update) (primary): SQLAlchemy project, SQLAlchemy 2.0.58, checked 2026-11-24
- [Legacy Query API](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html): SQLAlchemy project, SQLAlchemy 2.0.58, checked 2026-11-24

<a id="persistence.trailing-debounce"></a>
### Trailing-edge debounce

Stories: 8.8.2 | Phase: P1
Keywords: debounce, coalescing, call_later, per-path timer

Each new event for a path cancels the old timer and starts a new one.
The fetch runs once, after the path is quiet.
Keep one timer per path.
Implement it with loop.call_later and TimerHandle.cancel.

Sources:
- [Event Loop: call_later](https://docs.python.org/3/library/asyncio-eventloop.html) (primary): Python Software Foundation, Python 3.15.2, checked 2026-11-24
