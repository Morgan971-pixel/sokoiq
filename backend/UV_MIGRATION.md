# uv Migration

## Before (pip)

- Dependency source: `requirements.txt` (12 top-level entries)
- Install command: `pip install --no-cache-dir -r requirements.txt`
- Measured: fresh venv, `time pip install --no-cache-dir -r requirements.txt`
- Result: 6.10s wall clock, 36 packages installed

## After (uv)

- Dependency source: `pyproject.toml` (project name `sokoiq-backend`, `requires-python = ">=3.11"` to match the Dockerfile's `python:3.11-slim` base) plus `uv.lock`
- Install command: `uv sync`
- Measured: removed `.venv`, `time uv sync` from scratch
- Result: 0.22s wall clock, 36 packages installed
- Note: this number benefits from uv's shared local package cache (`~/.cache/uv`), which is part of its speed advantage over pip's cold, uncached installs. Not a strictly apples-to-apples cold-cache comparison, but representative of repeated local/CI installs.

## Dockerfile changes

Replaced the pip install step with the standard uv Docker pattern: copy the uv binary from the official uv image, copy only `pyproject.toml` and `uv.lock` first and run `uv sync --frozen --no-install-project` (so the dependency layer caches independently of source changes), then copy the rest of the source and run `uv sync --frozen` again, then prepend `/app/.venv/bin` to `PATH` so the existing `CMD` (`uvicorn ...`) resolves to the venv's interpreter unchanged. Base image and CMD are otherwise untouched.

**Not verified with a real `docker build`** in this environment (no Docker daemon available here). The Dockerfile syntax and the `uv sync` steps were validated locally (`uv sync`, `uv run pytest`) but the multi-stage `COPY --from=ghcr.io/astral-sh/uv:latest` step and the full image build were not. Build this locally or let Railway build it on the PR branch before merging to confirm.

## railway.toml

No change. `[build] builder = "DOCKERFILE"` points at the Dockerfile by path only; it contains no direct reference to `requirements.txt`, `pip`, or an explicit build/start command that bypasses the Dockerfile. All the actual risk lives in the Dockerfile edit above.

## requirements.txt

Kept, not deleted. Regenerated as a generated artifact via `uv export --no-hashes --no-dev -o requirements.txt` so it stays in sync with `uv.lock`. Reason: Docker build could not be tested locally (no Docker available), so there is no verified proof the new uv-based Dockerfile builds cleanly on Railway. Keeping requirements.txt as a fallback costs nothing and gives a reviewer/Railway a known-good path to revert to if the uv build step fails in Railway's environment. Regenerate it any time with the same `uv export` command after dependency changes; do not hand-edit it.

## Test result

`uv run pytest -v`: 54 passed, 0 failed.

## Takeaway

Dependency management and local installs are now faster and lockfile-pinned via uv, but the Dockerfile's build-stage change is the one part of this migration that was not build-tested end to end here and needs a real Railway/Docker build check before merge.
