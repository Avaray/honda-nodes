# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-10-07
### Added
- **Download Files — CivitAI & HuggingFace API Token Inputs**: Added a collapsible "API Tokens" section at the bottom of the Download Files node. It contains plain-text fields for a CivitAI token and a HuggingFace token. Tokens are stored in the workflow JSON via hidden socketless widgets and are never passed as connected inputs (which would conflict with the node's manual-only execution model).
- **Download Files — Authenticated Downloads**: The node now automatically appends the CivitAI token as a `?token=` query parameter so it survives cross-domain redirects to Cloudflare R2 / AWS S3 storage. HuggingFace downloads are authenticated via the `Authorization: Bearer` header.
- **Download Files — Real Filename Resolution**: The URL input now resolves and displays the real filename from the `Content-Disposition` response header (supports RFC 5987 `filename*=` and plain `filename=` formats), falling back to the final redirect URL path. This means API-style download URLs correctly show the model filename instead of the numeric ID.

### Changed
- **Download Files — Token Input UX**: The "API Tokens" `<summary>` label turns bold green in real time whenever at least one token field contains a value, providing instant at-a-glance feedback even while the section is collapsed.
- **Download Files — URL Validation**: `check_url` now attempts a `HEAD` request first and falls back to a plain `GET` if the server returns `403` or `405`. This fixes free Civitai models (which return `403` to `HEAD`) incorrectly showing as invalid.

### Fixed
- **Download Files — Free Models Broken by Token**: Appending an `Authorization: Bearer` header alongside `?token=` caused AWS S3 / Cloudflare R2 to return `400 Bad Request`, breaking downloads for all free Civitai models when a token was configured. The `Authorization` header is no longer sent for Civitai URLs; only the `?token=` query parameter is used.
- **Download Files — False Positive Auth Detection**: The login-redirect check previously flagged any URL containing the string `"auth"`, incorrectly blocking downloads redirected to S3 pre-signed URLs with `Authorization=...` in the query string. The check now inspects only the host (`auth.civitai.com`) and path (`/login`, `/authorize`).
- **Download Files — Token Scope Error**: `getTokens()` was defined outside the closure visible to `updateUI` event handlers, causing a silent `ReferenceError` on every download or check attempt. Moved to the correct inner scope.
- **Download Files — Missing Mode Variable**: A `NameError` on the `mode` variable (`"ab"` vs `"wb"`) caused every download attempt to fail immediately with a red progress bar. The variable was accidentally dropped during an earlier refactor and has been restored.

## [1.1.0] - 2026-10-06
### Added
- **Array Node Group**: Added 9 new nodes for working with collections (represented as newline-separated strings): `Array From Text`, `Array To Text`, `Array Get Item`, `Array Slice`, `Array Length`, `Array Filter`, `Array Includes`, `Array Is Empty`, and `Array For Each`.
- **Image Size Node**: Added a node to extract width and height from an image tensor.
- **File Hash Node**: Added a fast, memory-efficient node to calculate MD5 or SHA-256 hashes of files using native Python `hashlib`.
- **Print to Console Node**: Added a tool node for debugging that prints values to the ComfyUI server console.
- **Download Files — Resumable Downloads**: Interrupted downloads now resume from where they left off using HTTP `Range` headers. Canceling a download no longer deletes the partial file.
- **Download Files — URL Validation**: The URL input field now automatically validates the URL on blur/Enter using a lightweight `HEAD` request (with a `GET Range=0-0` fallback). Invalid or unreachable URLs are highlighted in red.
- **Download Files — Duplicate Detection**: Adding two entries that would result in the same file path is now detected instantly. Duplicated rows are highlighted with an orange border and their download buttons are disabled.

### Changed
- **Download Files UX**:
  - Reorganized the button layout to use a flexible bottom bar.
  - "Add File" and "Download All Files" buttons sit side-by-side and wrap only when space is insufficient.
  - Download button visually dims (grayscale) when inputs are incomplete.
  - URL fields collapse to show only the filename when not focused.
  - Progress bar and row border turn green when a download successfully completes.
  - Skips the confirmation dialog when removing empty download entries.
  - "Download All Files" is greyed out when no valid, non-duplicate entry exists.
- **Download Files — Workflow Integration**: The node no longer triggers downloads automatically when the workflow runs. Downloads are exclusively manual via the UI buttons.
- **Documentation & Registry**: Updated README with screenshot and improved installation instructions. Updated `pyproject.toml` to meet ComfyUI Registry standards.

### Fixed
- **Download Files Cancellation**: Overhauled event handling (using `mousedown` event delegation) to resolve DOM race conditions that prevented canceling individual active downloads.
- **Download Files — Duplicate Styling**: Duplicate warning now correctly overrides the "done" (green) status styling so already-downloaded duplicates are still flagged.
- **Download Files — Status After Delete**: Deleting a duplicate entry now triggers a file-existence check so the remaining entry correctly reflects its on-disk state.
- **Print to Console Execution**: Bypassed ComfyUI caching using `IS_CHANGED` so the node reliably prints during repeated workflow runs.
- **UI Overflow**: Fixed CSS flexbox layout issues where button text would spill out on narrow node widths.
- **Registry CI**: Fixed the GitHub Actions version-check step to use the correct `api.comfy.org` JSON endpoint instead of scraping the HTML registry page.

## [1.0.0] - 2026-10-06
### Added
- Initial release featuring metadata nodes, text logic, file system operations, and download capabilities.
