# Honda Nodes for ComfyUI

[![ComfyUI Registry](https://img.shields.io/badge/ComfyUI-Registry-blue)](https://registry.comfy.org/publishers/avaray/nodes/honda-nodes)

A specialized node pack for [ComfyUI](https://github.com/comfyanonymous/ComfyUI), heavily focused on **image metadata editing and manipulation**, and fully optimized for the new **ComfyUI V3 API** (Nodes 2.0).

At its core, this project is built around the integrated `ime` tool for secure, lossless metadata operations. Think of the other nodes (JSON parsing, text manipulation, file system operations, and future logic components) as foundational building blocks. They exist to support the core metadata tools, allowing you to orchestrate complex automation pipelines, process data effectively, and perform format conversions directly within your workflows.

## Features

- **Metadata (Core)**: Extract, write, and convert image metadata securely without touching image pixels. Native integration with the fast `ime` backend.
- **Image**: Custom Image Load and Save nodes with built-in metadata support and watermarking capabilities.
- **JSON**: Powerful JSON parsing and manipulation to handle complex metadata structures (Get/Set/Delete keys, Merge objects, Validate, Preview).
- **Text**: Advanced text manipulation for formatting prompts and tags (Concatenate, Replace, Split, Switch, Case Switch, Regex Match, Preview).
- **File System**: Native file and directory operations for managing batches (List Files, Move, Rename, Delete, Read, Path Normalization).
- **Tools**: Bulk file downloading directly from the node graph.
- **Logic**: Control flow and automation logic nodes (TODO: coming soon!).

## Installation

### Method 1: ComfyUI Manager (Recommended)
This package is officially available in the ComfyUI Registry!
1. Open ComfyUI and click on **Manager**.
2. Click **Custom Nodes Manager**.
3. Search for `Honda Nodes` (or `honda-nodes`).
4. Click **Install**. The Manager will automatically handle setup and download the required fast background binaries (`jq` and `ime`).
5. Restart ComfyUI.

You can view the official package page here: 
[https://registry.comfy.org/publishers/avaray/nodes/honda-nodes](https://registry.comfy.org/publishers/avaray/nodes/honda-nodes)

### Method 2: Manual
1. Clone this repository into your `ComfyUI/custom_nodes/` directory.
2. Open a terminal inside the `honda-nodes` directory and use your ComfyUI Python environment to execute the setup installer:
   ```bash
   ..\..\..\python_embeded\python.exe install.py
   ```
3. Restart ComfyUI.

## License

MIT - See [LICENSE](LICENSE) for details.
