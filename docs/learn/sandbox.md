<!-- Generated from sources.yaml by api/scripts/learn_index.py. Do not edit by hand. -->
# Learning index: sandbox

<a id="sandbox.asyncio-timeout"></a>
### asyncio.timeout

Stories: 4.6.3 | Phase: P1
Keywords: asyncio.timeout, TimeoutError, wait_for, cancellation

asyncio.timeout is an async context manager added in Python 3.11.
At the deadline it cancels the task and raises TimeoutError.
Catch TimeoutError outside the async with block.
Code that swallows CancelledError breaks it.

Sources:
- [Coroutines and Tasks: Timeouts](https://docs.python.org/3/library/asyncio-task.html) (primary): Python Software Foundation, Python 3.15 docs, checked 2026-11-24

<a id="sandbox.caddy-admin-api"></a>
### Caddy admin API

Stories: 4.4.2 | Phase: P1
Keywords: admin API, POST /load, /config/ path, localhost:2019

The admin endpoint listens on localhost:2019 by default.
POST /load replaces the whole config and rolls back on error.
/config/[path] reads or patches one part of the config.
Bind it to a Unix socket if untrusted code runs nearby.

Sources:
- [API](https://caddyserver.com/docs/api) (primary): Caddy project, Caddy 2.x docs, no version shown, checked 2026-11-24

<a id="sandbox.caddy-forward-auth"></a>
### Caddy forward_auth

Stories: 4.4.2 | Phase: P1
Keywords: forward_auth, copy_headers, session token check, auth gateway

Caddy sends a copy of each request to an auth gateway.
A 2xx answer lets the request continue.
Any other answer goes back to the client.
copy_headers passes chosen gateway headers to the app.

Sources:
- [forward_auth (Caddyfile directive)](https://caddyserver.com/docs/caddyfile/directives/forward_auth) (primary): Caddy project, Caddy 2.x docs, no version shown, checked 2026-11-24

<a id="sandbox.caddy-reverse-proxy"></a>
### Caddy reverse_proxy

Stories: 4.4.2 | Phase: P1
Keywords: reverse_proxy, dynamic upstreams, WebSocket upgrade, SSRF

The directive proxies requests to one or more backends.
Dynamic upstreams come from modules, for example A or SRV records.
WebSocket upgrades are tunneled both ways.
Map the upstream yourself. Do not trust the Host header.

Sources:
- [reverse_proxy (Caddyfile directive)](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy) (primary): Caddy project, Caddy 2.11.x docs, checked 2026-11-24

<a id="sandbox.caddy-stream-close-delay"></a>
### Caddy stream_close_delay

Stories: 4.4.2 | Phase: P1
Keywords: stream_close_delay, config reload, WebSocket close, stream_timeout

By default a config reload closes WebSocket connections.
stream_close_delay keeps them open for a set time.
The docs suggest a value such as 5m as a start.
This confirms the study guide pitfall about terminals.

Sources:
- [reverse_proxy (Caddyfile directive)](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy) (primary): Caddy project, Caddy 2.11.x docs, checked 2026-11-24

<a id="sandbox.capabilities"></a>
### Linux capabilities

Stories: 4.1.2, 4.2.2 | Phase: P1
Keywords: CAP_CHOWN, CAP_FOWNER, CAP_DAC_OVERRIDE, cap-drop

Root power is split into separate switches.
CHOWN changes owners; FOWNER skips owner checks such as chmod and timestamps.
DAC_OVERRIDE skips file permission checks.
Dropping all caps removes these even for root.

Sources:
- [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24

<a id="sandbox.cgroup-v2-limits"></a>
### cgroup v2 resource limits

Stories: 4.1.2 | Phase: P1
Keywords: memory.max, pids.max, cpu.max, memory.high, OOM

memory.max is a hard cap that can trigger the OOM killer.
memory.high only throttles.
pids.max makes fork fail with EAGAIN.
cpu.max holds quota and period in microseconds.

Sources:
- [Control Group v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) (primary): The Linux kernel documentation, kernel docs (current), checked 2026-11-24

<a id="sandbox.csp-frame-ancestors"></a>
### CSP frame-ancestors

Stories: 4.4.2 | Phase: P1
Keywords: frame-ancestors, Content-Security-Policy, X-Frame-Options, clickjacking

The directive says which parents may embed a page.
It replaces X-Frame-Options and does not fall back to default-src.
It works only as an HTTP header, not in a meta tag.
Set it so the IDE origin may frame the preview.

Sources:
- [CSP: frame-ancestors](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors) (primary): MDN Web Docs (Mozilla), CSP Level 3; MDN live docs, checked 2026-11-24

<a id="sandbox.defusedxml"></a>
### defusedxml for untrusted XML

Stories: 4.6.1 | Phase: P1
Keywords: defusedxml, XXE, billion laughs, JUnit XML

defusedxml replaces stdlib XML parsers with hardened ones.
It covers entity expansion, external entities and DTD retrieval.
JUnit files come from learner code, so parse them with it.
The README shows the last release as 0.8.0.

Sources:
- [defusedxml README](https://github.com/tiran/defusedxml/blob/main/README.md) (primary): Christian Heimes (project maintainer), 0.8.0 (latest changelog entry), checked 2026-11-24
- [XML Processing Modules: XML security](https://docs.python.org/3/library/xml.html): Python Software Foundation, Python 3.15 docs, checked 2026-11-24

<a id="sandbox.docker-embedded-dns"></a>
### Docker embedded DNS server

Stories: 4.4.1 | Phase: P1
Keywords: 127.0.0.11, embedded DNS, container name resolution, DNS forwarding

User-defined networks use a DNS server at 127.0.0.11.
It resolves container names and aliases on that network.
It forwards other names to the host DNS servers.
Check whether an internal network still leaks names this way.

Sources:
- [Networking overview](https://docs.docker.com/engine/network/) (primary): Docker Inc., Docker Engine docs, no version shown, checked 2026-11-24

<a id="sandbox.docker-internal-network"></a>
### Docker internal networks

Stories: 4.4.1 | Phase: P1
Keywords: --internal, network create, no default route, isolation

An internal network has no default route and no outside traffic.
Containers on it still reach each other and the gateway IP.
The host can reach every container IP directly.
Attach only the proxy, never the API or database.

Sources:
- [docker network create](https://docs.docker.com/reference/cli/docker/network/create/) (primary): Docker Inc., Docker Engine docs, no version shown, checked 2026-11-24

<a id="sandbox.docker-network-none"></a>
### Docker none network driver

Stories: 4.6.1 | Phase: P1
Keywords: --network none, loopback only, network isolation

With --network none the container has only a loopback interface.
It has no other network access.
Use it for the clean-copy test runner.

Sources:
- [None network driver](https://docs.docker.com/engine/network/drivers/none/) (primary): Docker Inc., Docker Engine docs, no version shown, checked 2026-11-24

<a id="sandbox.docker-run-hardening-flags"></a>
### docker run hardening flags

Stories: 4.1.2 | Phase: P1
Keywords: --cap-drop, no-new-privileges, --read-only, --pids-limit, --tmpfs, --user

Flags combine to shrink what a container can do.
Drop caps, set no-new-privileges, make the rootfs read-only.
Add pids and memory limits and a non-root user.
Use tmpfs for the paths that must be writable.

Sources:
- [docker container run](https://docs.docker.com/reference/cli/docker/container/run/) (primary): Docker Inc., Docker Engine docs (current), checked 2026-11-24

<a id="sandbox.docker-sdk-engine"></a>
### Docker Engine API and SDKs

Stories: 4.1.2, 4.6.1 | Phase: P1
Keywords: Engine API, SDK, version negotiation, docker-py

The daemon exposes a REST API; official SDKs exist for Go and Python.
Pin or negotiate the API version in code.
The API is the way to start and limit containers from the platform.

Sources:
- [Develop with Docker Engine SDKs](https://docs.docker.com/reference/api/engine/sdk/) (primary): Docker Inc., Docker Engine docs (current), checked 2026-11-24

<a id="sandbox.docker-volume-copyup"></a>
### Docker volume copy-up

Stories: 4.1.2, 4.5.2 | Phase: P1
Keywords: named volume, copy-up, volume-nocopy, mount over existing files

An empty named volume gets the image files at the mount path on first use.
A non-empty volume hides existing files instead.
The volume-nocopy option stops the copy.
This affects shared code and socket volumes.

Sources:
- [Volumes](https://docs.docker.com/engine/storage/volumes/) (primary): Docker Inc., Docker Engine docs (current), checked 2026-11-24

<a id="sandbox.execve-argv"></a>
### execve with an argv array

Stories: 4.3.6 | Phase: P1
Keywords: execve, argv, no shell, E2BIG, command injection

execve takes the program, an argv array and an envp array.
Both arrays end with a null pointer.
No shell parses the strings, so no injection through them.
Total size is capped; too much gives E2BIG.

Sources:
- [execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24
- [std::process::Command](https://doc.rust-lang.org/std/process/struct.Command.html): The Rust project, Rust 1.100.0, checked 2026-11-24

<a id="sandbox.globset"></a>
### globset glob matching

Stories: 4.3.2, 4.2.3 | Phase: P1
Keywords: glob, globset, literal_separator, gitignore semantics

globset matches paths against one glob or a set of globs.
It reports all matching patterns.
** is valid only as a whole path component.
literal_separator controls whether * crosses slashes; this causes dialect mismatch with Python.

Sources:
- [globset](https://docs.rs/globset/latest/globset/) (primary): ripgrep project (BurntSushi), globset 0.4.22, checked 2026-11-24

<a id="sandbox.governor"></a>
### governor rate limiter

Stories: 4.3.3 | Phase: P1
Keywords: governor, rate limit, GCRA, token check

governor is a fast Rust rate limiting library.
It uses the Generic Cell Rate Algorithm.
The terminal listener can limit connection and message rates per key.
Pair it with token checks.

Sources:
- [governor](https://docs.rs/governor/latest/governor/) (primary): governor project, governor 0.10.4, checked 2026-11-24

<a id="sandbox.grep-searcher"></a>
### grep-searcher crate

Stories: 4.3.2, 4.3.6 | Phase: P1
Keywords: ripgrep internals, grep-searcher, grep-regex, in-process search

grep-searcher is ripgrep's line-oriented search library.
It reads input, applies a matcher and sends results to a sink.
It pairs with grep-regex.
Using it avoids a subprocess and the risks of flags like --pre.

Sources:
- [grep_searcher](https://docs.rs/grep-searcher/latest/grep_searcher/) (primary): ripgrep project (BurntSushi), grep-searcher 0.1.18, checked 2026-11-24

<a id="sandbox.iframe-sandbox"></a>
### iframe sandbox attribute

Stories: 4.4.2 | Phase: P1
Keywords: iframe sandbox, allow-scripts, allow-same-origin, separate origin

An empty sandbox value applies all restrictions.
Tokens lift single restrictions, for example allow-scripts.
allow-scripts with allow-same-origin on same-origin content defeats the sandbox.
Serve untrusted content from a separate origin.

Sources:
- [<iframe>: The Inline Frame element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe) (primary): MDN Web Docs (Mozilla), MDN live docs, no version shown, checked 2026-11-24

<a id="sandbox.inode-timestamps"></a>
### Inode timestamps

Stories: 4.2.2 | Phase: P1
Keywords: atime, mtime, ctime, stat, trace removal

Each inode holds atime, mtime and ctime.
ctime changes on any metadata change such as chmod or chown.
So ctime can show that a file was touched later.
Writing a file also updates mtime.

Sources:
- [inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24

<a id="sandbox.inotify"></a>
### inotify and IN_Q_OVERFLOW

Stories: 4.3.2 | Phase: P1
Keywords: inotify, IN_Q_OVERFLOW, max_user_watches, file watch

inotify reports file events through a queue.
If the queue overflows, an IN_Q_OVERFLOW event arrives and events are lost, so rescan.
max_user_watches limits watches per user.
Rename produces paired events.

Sources:
- [inotify(7)](https://man7.org/linux/man-pages/man7/inotify.7.html) (primary): Linux man-pages project, Linux man-pages 6.19, checked 2026-11-24

<a id="sandbox.jsonc-parsing"></a>
### Parsing JSON with comments

Stories: 4.3.4 | Phase: P1
Keywords: jsonc, comments, tasks.json, jsonc-parser

The task file allows comments and may end lists with commas.
Plain JSON parsers reject such files.
The jsonc-parser crate accepts comments by default; a flag turns that off.
Pick strictness on purpose.

Sources:
- [jsonc_parser](https://docs.rs/jsonc-parser/latest/jsonc_parser/) (primary): dprint (docs.rs), jsonc-parser 0.34.0, checked 2026-11-24

<a id="sandbox.length-delimited-codec"></a>
### LengthDelimitedCodec framing

Stories: 4.3.1 | Phase: P1
Keywords: framing, length prefix, tokio-util codec, max frame length

Length-delimited framing turns a byte stream into whole frames.
Each frame has a length prefix, so readers need no manual buffering.
Set a maximum frame length to reject oversized input.
Combine with serde for the agent protocol.

Sources:
- [tokio_util::codec::length_delimited](https://docs.rs/tokio-util/latest/tokio_util/codec/length_delimited/index.html) (primary): Tokio project, tokio-util 0.7.20, checked 2026-11-24

<a id="sandbox.notify-crate"></a>
### notify crate and debouncer

Stories: 4.3.2 | Phase: P1
Keywords: notify, file watcher, debouncer, rename events

notify is the cross-platform file watcher crate.
notify-debouncer-full groups bursts, joins rename chains and drops duplicate events.
The page lists platform limits, such as inotify watch counts.
Exclude big dirs like node_modules.

Sources:
- [notify](https://docs.rs/notify/latest/notify/) (primary): notify-rs project, notify 9.0.0, checked 2026-11-24
- [notify_debouncer_full](https://docs.rs/notify-debouncer-full/latest/notify_debouncer_full/) (primary): notify-rs project, notify-debouncer-full 0.8.0, checked 2026-11-24

<a id="sandbox.openat2"></a>
### openat2 and RESOLVE_BENEATH

Stories: 4.3.2 | Phase: P1
Keywords: path traversal, symlink escape, RESOLVE_BENEATH, RESOLVE_NO_SYMLINKS

openat2 opens a path relative to a directory fd with resolve flags.
RESOLVE_BENEATH blocks any escape from that directory, including absolute symlinks.
RESOLVE_NO_SYMLINKS rejects symlinks in every component.
The call dates from Linux 5.6.

Sources:
- [openat2(2)](https://man7.org/linux/man-pages/man2/openat2.2.html) (primary): Linux man-pages project, Linux man-pages 6.19, checked 2026-11-24

<a id="sandbox.pid1-zombie-reaping"></a>
### PID 1 duties and docker --init

Stories: 4.3.1 | Phase: P1
Keywords: PID 1, zombie, docker run --init, signal handling

A container's first process acts as init.
It must reap exited children, or zombies pile up, and handle signals.
docker run --init puts a small init at PID 1 to do this.
The agent can use it or implement reaping itself.

Sources:
- [docker container run](https://docs.docker.com/reference/cli/docker/container/run/) (primary): Docker Inc., Docker docs (current), checked 2026-11-24

<a id="sandbox.portable-pty"></a>
### portable-pty crate

Stories: 4.3.3 | Phase: P1
Keywords: portable-pty, PTY, spawn_blocking, cross-platform

portable-pty offers traits for PTY work across platforms.
The docs page does not say if I/O blocks; the guide says it does, so test it.
Wrap its readers and writers in spawn_blocking.
Alternatives are pty-process and AsyncFd.

Sources:
- [portable_pty](https://docs.rs/portable-pty/latest/portable_pty/) (primary): WezTerm project, portable-pty 0.9.0, checked 2026-11-24

<a id="sandbox.proc-net-tcp"></a>
### /proc/net/tcp socket table

Stories: 4.3.5 | Phase: P1
Keywords: listening ports, proc net tcp, hex address, socket inode

The file lists TCP sockets, listeners first.
Addresses and ports are in hex.
A two-digit hex state code marks listen or established.
The inode column links a socket to the owning process.
The kernel page marks the file as deprecated.

Sources:
- [The proc/net/tcp and proc/net/tcp6 variables](https://docs.kernel.org/networking/proc_net_tcp.html) (primary): The Linux kernel documentation, kernel docs (current), checked 2026-11-24

<a id="sandbox.proc-status-fields"></a>
### /proc/PID/status fields

Stories: 4.1.2 | Phase: P1
Keywords: CapEff, CapBnd, NoNewPrivs, Seccomp, verify hardening

Shows capability masks: CapEff, CapPrm, CapBnd and others.
Seccomp field: 0 off, 1 strict, 2 filter.
NoNewPrivs shows the no_new_privs bit.
Use it to check a hardened container from inside.

Sources:
- [proc_pid_status(5)](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24

<a id="sandbox.process-groups-killpg"></a>
### Process groups and killpg

Stories: 4.3.3, 4.3.4 | Phase: P1
Keywords: killpg, process group, SIGTERM, SIGKILL

killpg sends a signal to every process in a group.
On Linux it calls kill with a negated group id.
Start each task in its own group, send SIGTERM, then SIGKILL after a grace period.
This stops orphaned dev servers.

Sources:
- [killpg(3)](https://man7.org/linux/man-pages/man3/killpg.3.html) (primary): Linux man-pages project, Linux man-pages 6.19, checked 2026-11-24

<a id="sandbox.procfs-crate"></a>
### procfs crate for port detection

Stories: 4.3.5 | Phase: P1
Keywords: procfs, TcpNetEntry, net::tcp, Linux /proc

Rust crate that reads /proc as typed data.
The net module has tcp() and tcp6() with TcpNetEntry rows.
This avoids hand parsing of the text tables.
Linux only.

Sources:
- [procfs::net](https://docs.rs/procfs/latest/procfs/net/index.html) (primary): procfs crate (docs.rs), procfs 0.18.0, checked 2026-11-24
- [procfs](https://docs.rs/procfs/latest/procfs/): procfs crate (docs.rs), procfs 0.18.0, checked 2026-11-24

<a id="sandbox.procrastinate-queues-locks"></a>
### Procrastinate queues and locks

Stories: 4.6.3, 8.5.2 | Phase: P1
Keywords: procrastinate, lock, queue, lock_mode

Jobs with the same lock never run at the same time.
The default ordered mode also keeps lock order.
If no worker reads a queue, jobs on the same lock stay blocked.
mutex mode does not fix that blocked-queue case.

Sources:
- [Use locks](https://procrastinate.readthedocs.io/en/stable/howto/advanced/locks.html) (primary): Procrastinate project, stable docs, no version shown, checked 2026-11-24

<a id="sandbox.protected-links-sysctl"></a>
### fs.protected_hardlinks and protected_symlinks

Stories: 4.2.3 | Phase: P1
Keywords: protected_hardlinks, protected_symlinks, sysctl, TOCTOU

Both are host sysctls under /proc/sys/fs.
protected_hardlinks stops links to files the user does not own or access.
protected_symlinks limits following links in sticky world-writable directories.
A container cannot set them. The host kernel decides.

Sources:
- [Documentation for /proc/sys/fs](https://docs.kernel.org/admin-guide/sysctl/fs.html) (primary): The Linux Kernel documentation, Linux 7.4.0-rc4 docs, checked 2026-11-24

<a id="sandbox.pty-session"></a>
### pseudoterminals (pty(7))

Stories: 4.3.3 | Phase: P1
Keywords: pty, master slave, terminal, session

A pseudoterminal is a linked master and slave device pair.
The slave acts like a terminal; the program on the master drives it.
The agent holds the master and runs bash on the slave.
Session setup uses setsid and a controlling terminal.

Sources:
- [pty(7)](https://man7.org/linux/man-pages/man7/pty.7.html) (primary): Linux man-pages project, Linux man-pages 6.19, checked 2026-11-24

<a id="sandbox.pyc-files"></a>
### pyc cache files and source mtime

Stories: 4.2.2 | Phase: P1
Keywords: pyc, __pycache__, bytecode cache, source mtime

The pyc header stores the source mtime and size by default.
Python compares them with the source before it loads the cache.
Hash-based pyc files exist and do not use mtime.
Remove __pycache__ to avoid leaking patched file times.

Sources:
- [The import system: cached bytecode invalidation](https://docs.python.org/3/reference/import.html) (primary): Python Software Foundation, Python 3.15.2, checked 2026-11-24
- [PEP 552 - Deterministic pycs](https://peps.python.org/pep-0552/): Python Software Foundation, Final, checked 2026-11-24

<a id="sandbox.python-pathspec"></a>
### pathspec gitignore matching

Stories: 4.2.3, 4.3.2 | Phase: P1
Keywords: pathspec, gitignore, glob patterns, GitIgnoreSpec

The pathspec library matches paths with gitignore-style patterns.
PathSpec follows the documented rules. GitIgnoreSpec copies real git behavior.
Use match_file or match_files to test paths.
The Python side must agree with Rust globset.

Sources:
- [python-pathspec](https://github.com/cpburnz/python-pathspec) (primary): cpburnz (project maintainer), README, no version shown, checked 2026-11-24

<a id="sandbox.python-tarfile"></a>
### tarfile extraction filters

Stories: 4.6.1 | Phase: P1
Keywords: tarfile, extractall filter, data filter, path traversal

The data filter blocks absolute paths and paths outside the target.
It blocks links that point outside and device files.
Python 3.14 made data the default filter.
Filters do not stop disk or memory exhaustion. Extract to a fresh directory.

Sources:
- [tarfile - Read and write tar archive files](https://docs.python.org/3/library/tarfile.html) (primary): Python Software Foundation, Python 3.15.2, checked 2026-11-24

<a id="sandbox.rename-atomic"></a>
### rename(2) atomic replace

Stories: 4.3.2 | Phase: P1
Keywords: atomic write, rename, EXDEV, temp file

rename atomically replaces the target, so readers never see it missing.
Source and target must be on one filesystem, or it fails with EXDEV.
The new inode is owned by the writer, which affects lock invariants.
Write a temp file, fsync, then rename.

Sources:
- [rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html) (primary): Linux man-pages project, Linux man-pages 6.19, checked 2026-11-24

<a id="sandbox.rustix"></a>
### rustix syscall bindings

Stories: 4.3.1, 4.3.2 | Phase: P1
Keywords: rustix, syscalls, safe bindings, POSIX

rustix gives safe Rust wrappers for POSIX, Unix and Linux syscalls.
It can replace nix for peercred, signals and openat2.
It avoids libc in its default backend.
Check feature flags for each module.

Sources:
- [rustix](https://docs.rs/rustix/latest/rustix/) (primary): Bytecode Alliance, rustix 1.1.6, checked 2026-11-24

<a id="sandbox.seccomp"></a>
### seccomp syscall filtering

Stories: 4.1.2 | Phase: P1
Keywords: seccomp-bpf, syscall filter, no_new_privs, default profile

Seccomp limits which system calls a thread may make.
Filter mode uses a BPF program that can check arguments.
A filter needs no_new_privs or CAP_SYS_ADMIN.
Docker applies a default profile; a custom one comes via --security-opt.

Sources:
- [seccomp(2)](https://man7.org/linux/man-pages/man2/seccomp.2.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24
- [Seccomp security profiles for Docker](https://docs.docker.com/engine/security/seccomp/): Docker Inc., Docker Engine docs (current), checked 2026-11-24

<a id="sandbox.setrlimit"></a>
### setrlimit resource limits

Stories: 4.3.6 | Phase: P1
Keywords: RLIMIT_NPROC, RLIMIT_AS, RLIMIT_FSIZE, RLIMIT_CPU, prlimit

Each limit has a soft value and a hard cap.
NPROC makes fork fail with EAGAIN; root and some capabilities are exempt.
FSIZE sends SIGXFSZ; CPU sends SIGXCPU, then SIGKILL at the hard limit.
AS makes memory calls fail with ENOMEM.

Sources:
- [getrlimit(2)](https://man7.org/linux/man-pages/man2/setrlimit.2.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24

<a id="sandbox.shell-command-capture"></a>
### Capturing command output

Stories: 4.3.7 | Phase: P1
Keywords: stdout stderr capture, Command::output, Stdio, exit status

output() waits and captures stdout and stderr.
spawn() returns a handle and inherits stdio by default.
A non-zero exit is not an Err; read the status.
No shell is used unless you start one.

Sources:
- [std::process::Command](https://doc.rust-lang.org/std/process/struct.Command.html) (primary): The Rust project, Rust 1.100.0, checked 2026-11-24
- [tokio::process](https://docs.rs/tokio/latest/tokio/process/index.html): Tokio project (docs.rs), tokio 1.54.1, checked 2026-11-24

<a id="sandbox.sock-diag"></a>
### sock_diag netlink socket query

Stories: 4.3.5 | Phase: P1
Keywords: sock_diag, netlink, socket listing, ss

A netlink interface to ask the kernel about sockets.
It covers UNIX, IPv4 and IPv6 sockets.
It is an alternative to parsing /proc/net/tcp.
The ss tool uses it.

Sources:
- [sock_diag(7)](https://man7.org/linux/man-pages/man7/sock_diag.7.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24

<a id="sandbox.sticky-bit-permissions"></a>
### Sticky bit and file permissions

Stories: 4.2.3 | Phase: P1
Keywords: sticky bit, S_ISVTX, delete rename, directory owner

On a directory the sticky bit limits delete and rename.
Only the file owner, the directory owner, or a privileged process may do it.
So a root-owned sticky directory protects root-owned locked files.
A runner-owned directory breaks this protection.

Sources:
- [inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24

<a id="sandbox.thiserror"></a>
### thiserror derive macro

Stories: 4.3.1 | Phase: P1
Keywords: thiserror, Error derive, error enum, Rust errors

thiserror derives std::error::Error for an enum or struct.
It removes the Display and From boilerplate.
The project style requires it in Rust, with no unwrap or panic.
One enum per module keeps error codes fixed.

Sources:
- [thiserror](https://docs.rs/thiserror/latest/thiserror/) (primary): David Tolnay, thiserror 2.0.21, checked 2026-11-24

<a id="sandbox.tokio-asyncfd"></a>
### tokio AsyncFd

Stories: 4.3.3 | Phase: P1
Keywords: AsyncFd, readiness, clear_ready, raw fd

AsyncFd registers a raw Unix fd with Tokio's reactor.
Tasks can then await read or write readiness.
After WouldBlock, clear only the readiness that blocked.
Use it with nix::pty master fds.

Sources:
- [AsyncFd in tokio::io::unix](https://docs.rs/tokio/latest/tokio/io/unix/struct.AsyncFd.html) (primary): Tokio project, tokio 1.54.1, checked 2026-11-24

<a id="sandbox.tokio-mpsc-bounded"></a>
### Bounded tokio mpsc channel

Stories: 4.3.7 | Phase: P1
Keywords: mpsc, backpressure, bounded channel, event stream

Multi-producer, single-consumer queue between tasks.
A bounded channel makes senders wait when full.
This gives backpressure for the event stream.
Use blocking_send from sync code.

Sources:
- [tokio::sync::mpsc](https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html) (primary): Tokio project (docs.rs), tokio 1.54.1, checked 2026-11-24

<a id="sandbox.tokio-process"></a>
### tokio::process for agent tasks

Stories: 4.3.4 | Phase: P1
Keywords: tokio process, kill_on_drop, zombie, Child

Async wrapper over std Command for spawning tasks.
A dropped Child keeps running unless kill_on_drop is set.
Tokio reaps finished children only on a best-effort basis.
Await the child to the end for strict cleanup.

Sources:
- [tokio::process](https://docs.rs/tokio/latest/tokio/process/index.html) (primary): Tokio project (docs.rs), tokio 1.54.1, checked 2026-11-24

<a id="sandbox.tokio-select-cancel"></a>
### tokio select! and cancellation

Stories: 4.3.1 | Phase: P1
Keywords: select!, cancellation safety, CancellationToken, shutdown

select! waits on several futures and drops the losers.
A dropped branch can lose partial work, so branches must be cancellation safe.
mpsc recv is safe; read_exact and write_all are not.
Use it for the agent's accept loop and shutdown.

Sources:
- [select in tokio](https://docs.rs/tokio/latest/tokio/macro.select.html) (primary): Tokio project, tokio 1.54.1, checked 2026-11-24

<a id="sandbox.tokio-spawn-blocking"></a>
### tokio spawn_blocking

Stories: 4.3.3 | Phase: P1
Keywords: spawn_blocking, blocking thread pool, abort, runtime shutdown

spawn_blocking runs a closure on a dedicated thread pool.
It keeps blocking calls off the async executor.
Abort has no effect once the closure runs.
Runtime shutdown waits for started blocking tasks.

Sources:
- [spawn_blocking in tokio::task](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html) (primary): Tokio project, tokio 1.54.1, checked 2026-11-24

<a id="sandbox.tokio-unixlistener"></a>
### tokio UnixListener

Stories: 4.3.1 | Phase: P1
Keywords: UnixListener, unix socket, bind, accept, stale socket

Tokio's UnixListener binds a socket path and accepts UnixStream connections.
A leftover socket file makes bind fail, so the agent removes it first (an OS rule, not stated on this page).
The agent serves its protocol on one socket path.

Sources:
- [UnixListener in tokio::net](https://docs.rs/tokio/latest/tokio/net/struct.UnixListener.html) (primary): Tokio project, tokio 1.54.1, checked 2026-11-24

<a id="sandbox.tracing-json"></a>
### tracing-subscriber JSON output

Stories: 4.3.1 | Phase: P1
Keywords: tracing, JSON lines, structured logs, tracing-subscriber

tracing-subscriber's Json formatter prints one JSON object per line.
It fits the project's structured log rule.
Fields from events become JSON keys.
Custom fields such as event and subject go in as event fields.

Sources:
- [Json in tracing_subscriber::fmt::format](https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/format/struct.Json.html) (primary): Tokio project, tracing-subscriber 0.3.23, checked 2026-11-24

<a id="sandbox.unix-socket-peercred"></a>
### SO_PEERCRED and unix(7) sockets

Stories: 4.3.1, 8.4.2 | Phase: P1
Keywords: SO_PEERCRED, ucred, sun_path, peer credentials

SO_PEERCRED returns pid, uid and gid of the peer on a connected unix stream socket.
The agent can check who connects.
The values are those at connect or listen time.
Linux sun_path holds 108 bytes, so keep the socket path short.

Sources:
- [unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html) (primary): Linux man-pages project, Linux man-pages 6.19, checked 2026-11-24

<a id="sandbox.userns-rootless"></a>
### User namespaces and rootless Docker

Stories: 4.1.2 | Phase: P1
Keywords: user namespace, uid_map, rootless, subuid

A user namespace maps inner IDs to outer IDs; inner root is unprivileged outside.
uid_map lines hold inner start, outer start and length.
Rootless Docker runs the daemon as a normal user.
It needs newuidmap and subordinate ID ranges.

Sources:
- [user_namespaces(7)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24
- [Rootless mode](https://docs.docker.com/engine/security/rootless/) (primary): Docker Inc., Docker Engine docs (current), checked 2026-11-24

<a id="sandbox.utimensat"></a>
### utimensat sets file times

Stories: 4.2.2 | Phase: P1
Keywords: utimensat, UTIME_OMIT, UTIME_NOW, AT_SYMLINK_NOFOLLOW, ctime

Sets atime and mtime with nanosecond precision.
Explicit times need ownership or privilege; write access is not enough.
UTIME_NOW and UTIME_OMIT are special nanosecond values.
The call always sets ctime to now.

Sources:
- [utimensat(2)](https://man7.org/linux/man-pages/man2/utimensat.2.html) (primary): Linux man-pages project, man-pages 6.19, checked 2026-11-24
