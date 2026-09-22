# Honda Nodes - Ideas for Future Categories

## 1. 📁 File System (System Nodes)
Nodes dedicated to managing how files and directories are handled, which is often a pain point in complex ComfyUI workflows.
* **Create Directory:** Automatically generates timestamped folders (e.g., `outputs/2026-09-21/`) and outputs the path for your Save Image node.
* **List Files:** Takes a directory path and outputs a list of all files inside it (great for batch processing).
* **Move / Rename File:** Automatically moves or renames a file after it's generated, based on dynamic text inputs.

## 2. 🧮 Math & Logic
ComfyUI lacks built-in simple math operations, which are often needed to dynamically calculate resolutions, latent sizes, or batch counts.
* **Basic Math:** Add, subtract, multiply, or divide two numbers.
* **Resolution Calculator:** Input an aspect ratio (e.g., `16:9`) and a base pixel count (e.g., `1024`), and it outputs the exact Width and Height integers.
* **Randomizer:** Generates a random integer or float between a Min and Max value, or picks a random string from a list.

## 3. 🌐 Network & Webhooks
Since the extension is already excellent at working with CLI tools and raw data (like JSON), adding network capabilities would make it incredibly powerful for automation.
* **Send Webhook:** Takes a generated Image Path, some text (or JSON), and sends it to Discord, Telegram, or Slack using a Webhook URL.
* **HTTP Request:** A generic node (wrapping `curl`) that can make a GET or POST request to fetch external data (like a prompt from an API) and output it as a string to feed into JSON nodes.

## 4. 🧠 Prompt Engineering
Nodes specifically designed to manipulate and build complex prompts before they hit the CLIP Text Encode nodes.
* **Wildcard Resolver:** Takes a string like `A photo of a {cat|dog|bird}` and randomly picks one option.
* **Prompt Weighting:** A UI node where you input a keyword and a slider, and it automatically formats it into standard ComfyUI syntax (e.g., `(keyword:1.5)`).

## 5. 🛠️ CLI Wrappers (Execution)
A generic category for wrapping other standard lightweight CLI tools, following the successful implementation of `mex` and `jq`.
* **FFmpeg Video/Audio:** Extract a specific frame from a video, or extract audio from an MP4 file.
* **ImageMagick:** Perform quick, raw image operations (like resizing, format conversion, or watermarking) via CLI before loading them into ComfyUI tensors.
