**Level:** Initiative (split into epics, then stories)

**Purpose:** Run user code safely.

### Scope
- **Work container per run:** from the project image, issue patches applied (`git apply`) at start.
- **Isolation:** no internet, CPU/memory/process/disk limits, non-root, read-only root except the workspace.
- **IO:** file sync and terminal over WebSocket.
- **App server:** runs the project's run command. The port is exposed through a backend proxy at `/preview/<run_id>/`, protected by a session token (owner only).
- **Grading container:** fresh project image. Copy in **editable files only** from the user workspace, then mount and run hidden tests. User changes to tests or config are ignored.
- **Lifecycle:** idle timeout, max run time, cleanup after submit.

### Open questions
- One Docker host now; queue and workers later?
- Session length limits.
