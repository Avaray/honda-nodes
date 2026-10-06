# ⚡️ Honda Nodes

A specialized node pack for [ComfyUI](https://github.com/comfyanonymous/ComfyUI), heavily focused on **image metadata editing and manipulation**, and fully optimized for the new **ComfyUI V3 API** (Nodes 2.0).

![Example Nodes](https://raw.githubusercontent.com/Avaray/honda-nodes/refs/heads/main/.github/screenshots/screenshot.jpg)

At its core, this project is built around the integrated [IME](https://github.com/Avaray/image-metadata-editor) tool for secure, lossless metadata operations. Think of the other nodes (JSON parsing, text manipulation, file system operations, and future logic components) as foundational building blocks. They exist to support the core metadata tools, allowing you to orchestrate complex automation pipelines, process data effectively, and perform format conversions directly within your workflows.

## ✨ Features

- **Metadata (Core)**: Extract, write, and convert image metadata securely without touching image pixels. Native integration with the fast `ime` backend.
- **Image**: Custom Image Load and Save nodes with built-in metadata support and watermarking capabilities.
- **JSON**: Powerful JSON parsing and manipulation to handle complex metadata structures (Get/Set/Delete keys, Merge objects, Validate, Preview).
- **Text**: Advanced text manipulation for formatting prompts and tags (Concatenate, Replace, Split, Switch, Case Switch, Regex Match, Preview).
- **File System**: Native file and directory operations for managing batches (List Files, Move, Rename, Delete, Read, Path Normalization).
- **Tools**: Bulk file downloading directly from the node graph.
- **Logic**: Control flow and automation logic nodes (TODO: coming soon!).

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)

This package is officially available in the [ComfyUI Registry](https://registry.comfy.org/publishers/avaray/nodes/honda-nodes).

1. Open ComfyUI and click on **Extensions**.
2. From the dropdown menu in **Nodes Manager**, select **Node Pack**.
3. Search for `Honda Nodes` (or `honda-nodes`).
4. Click **Install**.
5. Restart ComfyUI.

### Method 2: Manual

1. Clone this repository into your `ComfyUI/custom_nodes/` directory.

    ```bash
    git clone --depth 1 https://github.com/Avaray/honda-nodes.git
    ```

2. Open a terminal inside the `honda-nodes` directory and use your ComfyUI Python environment to execute the setup installer:

   ```bash
   ..\..\..\python_embeded\python.exe install.py
   ```

3. Restart ComfyUI.

## 📝 License

This project is licensed under the [MIT License](LICENSE). 
