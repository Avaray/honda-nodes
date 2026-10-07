import os
import re
import json
import urllib.request
import threading
import shutil
from urllib.parse import urlparse, unquote

import folder_paths
from comfy_api.latest import io
from server import PromptServer
from aiohttp import web

ACTIVE_DOWNLOADS = {}
DOWNLOADS_LOCK = threading.Lock()


def get_filename_from_headers(response, original_url):
    """Extract the real filename from Content-Disposition, falling back to the resolved URL path."""
    cd = response.getheader("Content-Disposition", "")
    if cd:
        # RFC 5987 encoded: filename*=UTF-8''some%20file.safetensors
        m = re.search(r"filename\*\s*=\s*(?:[A-Za-z0-9\-]+'')?([^;\r\n]+)", cd, re.IGNORECASE)
        if m:
            return unquote(m.group(1).strip().strip('"\''))
        # Plain: filename="some file.safetensors"
        m = re.search(r'filename\s*=\s*["\']?([^"\';\r\n]+)["\']?', cd, re.IGNORECASE)
        if m:
            return m.group(1).strip()
            
    # Fall back to the final resolved URL path, or original if not available
    final_url = getattr(response, "url", original_url)
    filename = os.path.basename(urlparse(final_url).path)
    
    # If the URL ends with a directory or something like an ID (no extension), and we had an original fallback
    if not filename or filename in ("login", "authorize"):
        filename = os.path.basename(urlparse(original_url).path)
        
    return filename or "downloaded_file"


@PromptServer.instance.routes.post("/honda/tools/download/check")
async def api_check_downloads(request):
    data = await request.json()
    results = {}
    for item in data:
        url = item.get("url")
        directory = item.get("dir")
        if not url or not directory:
            continue

        if os.path.isabs(directory):
            target_dir = directory
        else:
            target_dir = os.path.join(folder_paths.base_path, directory)

        # Try to resolve the real filename from the server (Content-Disposition)
        filename = os.path.basename(urlparse(url).path) or "downloaded_file"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
            with urllib.request.urlopen(req, timeout=5) as resp:
                filename = get_filename_from_headers(resp, url)
        except Exception:
            pass

        target_path = os.path.join(target_dir, filename)
        results[url] = os.path.exists(target_path)

    return web.json_response({"status": "success", "results": results})

@PromptServer.instance.routes.post("/honda/tools/download/cancel")
async def api_cancel_download(request):
    data = await request.json()
    url = data.get("url")
    with DOWNLOADS_LOCK:
        if url in ACTIVE_DOWNLOADS:
            ACTIVE_DOWNLOADS[url]["cancel"] = True
    return web.json_response({"status": "cancelled"})

# We will register an API route to handle URL validation (e.g. check if file exists)
@PromptServer.instance.routes.post("/honda/tools/download/check_url")
async def api_check_url(request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return web.json_response({"status": "error", "valid": False, "filename": None})

    filename_fallback = os.path.basename(urlparse(url).path) or None

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as response:
            if "login" in getattr(response, "url", "").lower() or "auth" in getattr(response, "url", "").lower():
                return web.json_response({"status": "success", "valid": False, "filename": filename_fallback, "error": "auth_required"})
            filename = get_filename_from_headers(response, url)
            return web.json_response({"status": "success", "valid": response.getcode() < 400, "filename": filename})
    except urllib.error.HTTPError as e:
        # Some servers reject HEAD. Fallback to GET with Range 0-0.
        if e.code in (403, 405):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-0"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    if "login" in getattr(response, "url", "").lower() or "auth" in getattr(response, "url", "").lower():
                        return web.json_response({"status": "success", "valid": False, "filename": filename_fallback, "error": "auth_required"})
                    filename = get_filename_from_headers(response, url)
                    return web.json_response({"status": "success", "valid": response.getcode() < 400, "filename": filename})
            except Exception:
                pass
        return web.json_response({"status": "success", "valid": False, "filename": filename_fallback})
    except Exception:
        return web.json_response({"status": "success", "valid": False, "filename": filename_fallback})

# We will register an API route to handle manual downloads directly from the UI.
@PromptServer.instance.routes.post("/honda/tools/download")
async def api_download_file(request):
    data = await request.json()
    url = data.get("url")
    directory = data.get("directory")
    
    if not url or not directory:
        return web.json_response({"status": "error", "message": "Missing url or directory"}, status=400)

    # Normalize directory
    base_path = folder_paths.get_folder_paths("checkpoints")[0] if folder_paths.get_folder_paths("checkpoints") else folder_paths.base_path
    
    if os.path.isabs(directory):
        target_dir = directory
    else:
        target_dir = os.path.join(folder_paths.base_path, directory)
        
    os.makedirs(target_dir, exist_ok=True)

    def download_thread():
        nonlocal target_dir
        with DOWNLOADS_LOCK:
            ACTIVE_DOWNLOADS[url] = {"cancel": False}
        canceled = False
        try:
            # Open the connection first so we can read Content-Disposition for the real filename
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

            try:
                response = urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                raise e

            # Civitai and other sites redirect to a login page if a token is required
            if "login" in getattr(response, "url", "").lower() or "auth" in getattr(response, "url", "").lower():
                raise Exception("Authentication required. Append ?token=YOUR_CIVITAI_TOKEN to the URL.")

            # Resolve the real filename from headers (handles Civitai and similar API URLs)
            filename = get_filename_from_headers(response, url)
            target_path = os.path.join(target_dir, filename)

            # If a partial file exists under the real name, resume it
            initial_size = 0
            if os.path.exists(target_path):
                initial_size = os.path.getsize(target_path)
                response.close()
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                req.add_header("Range", f"bytes={initial_size}-")
                try:
                    response = urllib.request.urlopen(req)
                except urllib.error.HTTPError as e:
                    if e.code == 416:  # Already complete
                        PromptServer.instance.send_sync("honda_download_progress", {
                            "url": url, "progress": 100.0, "status": "done", "filename": filename
                        })
                        return
                    raise e

            is_partial = (response.getcode() == 206)
            if not is_partial:
                initial_size = 0


            content_length = int(response.getheader('Content-Length', 0))
            totalsize = content_length + initial_size if content_length > 0 else 0
            blocksize = 8192
            downloaded = initial_size

            def reporthook():
                if totalsize > 0:
                    percent = min(100.0, downloaded * 100.0 / totalsize)
                else:
                    percent = 0.0
                PromptServer.instance.send_sync("honda_download_progress", {
                    "url": url,
                    "progress": percent,
                    "status": "downloading"
                })

            with open(target_path, mode) as out_file:
                while True:
                    with DOWNLOADS_LOCK:
                        if ACTIVE_DOWNLOADS.get(url, {}).get("cancel", False):
                            canceled = True
                            break
                    buffer = response.read(blocksize)
                    if not buffer:
                        break
                    out_file.write(buffer)
                    downloaded += len(buffer)
                    # Report progress every few blocks to not spam WebSocket? 
                    # Let's just report every block as before.
                    reporthook()

            if canceled:
                # Do NOT delete the file if canceled, so we can resume later!
                PromptServer.instance.send_sync("honda_download_progress", {
                    "url": url, "progress": 0.0, "status": "idle", "filename": filename
                })
            else:
                PromptServer.instance.send_sync("honda_download_progress", {
                    "url": url, "progress": 100.0, "status": "done", "filename": filename
                })
        except Exception as e:
            PromptServer.instance.send_sync("honda_download_progress", {
                "url": url, "progress": 0.0, "status": "error", "error": str(e)
            })
        finally:
            with DOWNLOADS_LOCK:
                if url in ACTIVE_DOWNLOADS:
                    del ACTIVE_DOWNLOADS[url]

    threading.Thread(target=download_thread, daemon=True).start()
    return web.json_response({"status": "started"})


class HondaDownloadFiles(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_DownloadFiles",
            display_name="🛠️ Download Files",
            category="⚡️ Honda Nodes/🛠️ Tools",
            description="Downloads specified files to specified directories. Triggered manually from the node UI — does not run automatically when the workflow executes.",
            is_output_node=True,
            inputs=[
                io.String.Input(
                    "downloads_config",
                    default="[]",
                    socketless=True,
                    display_name="Downloads",
                    tooltip="Internal JSON configuration of downloads",
                ),
            ],
            outputs=[],
        )

    @classmethod
    def execute(cls, downloads_config: str = "[]") -> io.NodeOutput:
        # Downloads are triggered manually through the node UI.
        # This node intentionally does nothing when the workflow runs.
        return io.NodeOutput()
