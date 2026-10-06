import os
import json
import urllib.request
import threading
import shutil
from urllib.parse import urlparse

import folder_paths
from comfy_api.latest import io
from server import PromptServer
from aiohttp import web

ACTIVE_DOWNLOADS = {}
DOWNLOADS_LOCK = threading.Lock()

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
            
        filename = os.path.basename(urlparse(url).path) or "downloaded_file"
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
        return web.json_response({"status": "error", "valid": False})
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            return web.json_response({"status": "success", "valid": response.getcode() < 400})
    except urllib.error.HTTPError as e:
        # Some servers reject HEAD. Fallback to GET with Range 0-0.
        if e.code in (403, 405):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Range': 'bytes=0-0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    return web.json_response({"status": "success", "valid": response.getcode() < 400})
            except Exception:
                pass
        return web.json_response({"status": "success", "valid": False})
    except Exception:
        return web.json_response({"status": "success", "valid": False})

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
    
    # Get filename from URL
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = "downloaded_file"
        
    target_path = os.path.join(target_dir, filename)
    
    def download_thread():
        with DOWNLOADS_LOCK:
            ACTIVE_DOWNLOADS[url] = {"cancel": False}
        canceled = False
        try:
            initial_size = 0
            if os.path.exists(target_path):
                initial_size = os.path.getsize(target_path)

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            if initial_size > 0:
                req.add_header('Range', f'bytes={initial_size}-')

            try:
                response = urllib.request.urlopen(req)
                is_partial = (response.getcode() == 206)
            except urllib.error.HTTPError as e:
                if e.code == 416:  # Range Not Satisfiable (already fully downloaded)
                    PromptServer.instance.send_sync("honda_download_progress", {
                        "url": url, "progress": 100.0, "status": "done"
                    })
                    return
                raise e

            mode = 'ab' if is_partial else 'wb'
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
                    "url": url,
                    "progress": 0.0,
                    "status": "idle"
                })
            else:
                PromptServer.instance.send_sync("honda_download_progress", {
                    "url": url,
                    "progress": 100.0,
                    "status": "done"
                })
        except Exception as e:
            PromptServer.instance.send_sync("honda_download_progress", {
                "url": url,
                "progress": 0.0,
                "status": "error",
                "error": str(e)
            })
        finally:
            with DOWNLOADS_LOCK:
                if url in ACTIVE_DOWNLOADS:
                    del ACTIVE_DOWNLOADS[url]

    threading.Thread(target=download_thread, daemon=True).start()
    return web.json_response({"status": "started", "filename": filename})


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
