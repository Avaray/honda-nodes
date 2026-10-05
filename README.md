# Honda Nodes for ComfyUI

A comprehensive collection of utility nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI), fully optimized for the new **ComfyUI V3 API** (Nodes 2.0).

## Features

This package provides a wide variety of utility nodes across several categories:

- **Text**: Advanced text manipulation (Concatenate, Replace, Split, Switch, Case Switch, Regex Match, Preview).
- **File System**: Native file and directory operations (List Files, Move, Rename, Delete, Read, Path Normalization).
- **JSON**: Powerful JSON parsing and manipulation (Get/Set/Delete keys, Merge objects, Validate, Preview).
- **Metadata**: Extract, write, and convert image metadata securely without touching image pixels (powered by the integrated `ime` tool).
- **Image**: Custom Image Load and Save nodes with built-in metadata support and watermarking capabilities.
- **Tools**: Bulk file downloading directly from the node graph.

## Installation

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI and go to **Manager**.
2. Click **Install via Git URL**.
3. Paste the URL of this repository.
   ```
   https://github.com/honda-nodes/honda-nodes.git
   ```
4. The Manager will automatically clone the repository and run the setup script (`install.py`) to download necessary fast background binaries (`jq` and `ime`).
5. Restart ComfyUI.

### Method 2: Manual
1. Clone this repository into your `ComfyUI/custom_nodes/` directory.
2. Open a terminal inside the `honda-nodes` directory and use your ComfyUI Python environment to execute the installer:
   ```bash
   ..\..\..\python_embeded\python.exe install.py
   ```
3. Restart ComfyUI.

## License

MIT - See [LICENSE](LICENSE) for details.
