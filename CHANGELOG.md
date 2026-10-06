# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
