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

### Changed
- **Download Files UX**:
  - Reorganized the button layout to use a flexible bottom bar.
  - Download button visually dims (grayscale) when inputs are incomplete.
  - URL fields collapse to show only the filename when not focused.
  - Progress bar and row border turn green when a download successfully completes.
  - Skips the confirmation dialog when removing empty download entries.
- **Documentation & Registry**: Updated README and `pyproject.toml` to emphasize the pack's focus on image metadata editing and to meet ComfyUI Registry standards.

### Fixed
- **Download Files Cancellation**: Overhauled event handling (using `mousedown` event delegation) to resolve DOM race conditions that prevented canceling individual active downloads.
- **Print to Console Execution**: Bypassed ComfyUI caching using `IS_CHANGED` so the node reliably prints during repeated workflow runs.
- **UI Overflow**: Fixed CSS flexbox layout issues where button text would spill out on narrow node widths.

## [1.0.0] - 2026-10-06
### Added
- Initial release featuring metadata nodes, text logic, file system operations, and download capabilities.
