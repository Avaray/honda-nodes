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
            def reporthook(blocknum, blocksize, totalsize):
                if totalsize > 0:
                    percent = min(100.0, blocknum * blocksize * 100.0 / totalsize)
                else:
                    percent = 0.0
                    
                PromptServer.instance.send_sync("honda_download_progress", {
                    "url": url,
                    "progress": percent,
                    "status": "downloading"
                })

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
                totalsize = int(response.getheader('Content-Length', 0))
                blocksize = 8192
                blocknum = 0
                while True:
                    with DOWNLOADS_LOCK:
                        if ACTIVE_DOWNLOADS.get(url, {}).get("cancel", False):
                            canceled = True
                            break
                    buffer = response.read(blocksize)
                    if not buffer:
                        break
                    blocknum += 1
                    out_file.write(buffer)
                    reporthook(blocknum, blocksize, totalsize)
            
            if canceled:
                if os.path.exists(target_path):
                    os.remove(target_path)
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
            description="Downloads specified files to specified directories. Can be run manually from the UI or during workflow execution.",
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
        try:
            downloads = json.loads(downloads_config)
        except Exception:
            downloads = []
            
        # When workflow runs, we can optionally download any missing files synchronously.
        for item in downloads:
            url = item.get("url", "").strip()
            directory = item.get("dir", "").strip()
            if not url or not directory:
                continue
                
            if os.path.isabs(directory):
                target_dir = directory
            else:
                target_dir = os.path.join(folder_paths.base_path, directory)
                
            os.makedirs(target_dir, exist_ok=True)
            filename = os.path.basename(urlparse(url).path) or "downloaded_file"
            target_path = os.path.join(target_dir, filename)
            
            # If it already exists, skip
            if not os.path.exists(target_path):
                print(f"[Honda Nodes] Downloading {url} to {target_path}...")
                PromptServer.instance.send_sync("honda_download_progress", {
                    "url": url,
                    "progress": 0.0,
                    "status": "downloading"
                })
                try:
                    def reporthook(blocknum, blocksize, totalsize):
                        if totalsize > 0:
                            percent = min(100.0, blocknum * blocksize * 100.0 / totalsize)
                        else:
                            percent = 0.0
                        PromptServer.instance.send_sync("honda_download_progress", {
                            "url": url,
                            "progress": percent,
                            "status": "downloading"
                        })
                        
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
                        totalsize = int(response.getheader('Content-Length', 0))
                        blocksize = 8192
                        blocknum = 0
                        while True:
                            buffer = response.read(blocksize)
                            if not buffer:
                                break
                            blocknum += 1
                            out_file.write(buffer)
                            reporthook(blocknum, blocksize, totalsize)
                            
                    print(f"[Honda Nodes] Download complete: {filename}")
                    PromptServer.instance.send_sync("honda_download_progress", {
                        "url": url,
                        "progress": 100.0,
                        "status": "done"
                    })
                except Exception as e:
                    print(f"[Honda Nodes] Failed to download {url}: {e}")
                    PromptServer.instance.send_sync("honda_download_progress", {
                        "url": url,
                        "progress": 0.0,
                        "status": "error",
                        "error": str(e)
                    })
            else:
                # Tell UI it's done since it exists
                PromptServer.instance.send_sync("honda_download_progress", {
                    "url": url,
                    "progress": 100.0,
                    "status": "done"
                })

        return io.NodeOutput()
