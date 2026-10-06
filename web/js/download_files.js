import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const DOWNLOAD_STYLE = `
.honda-download-widget {
    display: flex;
    flex-direction: column;
    gap: 8px;
    box-sizing: border-box;
    width: 100%;
    color: var(--fg-color);
    font-family: sans-serif;
    overflow-y: auto;
}

.honda-download-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: rgba(0,0,0,0.2);
    padding: 6px;
    border-radius: 4px;
    border: 1px solid rgba(255,255,255,0.1);
}

.honda-download-row-inputs {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.honda-download-row-top {
    display: flex;
    gap: 4px;
    align-items: center;
}

.honda-download-btn-group {
    display: flex;
    gap: 2px;
    flex-shrink: 0;
}

.honda-download-input {
    flex: 1;
    min-width: 100px;
    background: var(--comfy-input-bg);
    color: var(--input-text);
    border: 1px solid var(--border-color);
    border-radius: 3px;
    padding: 4px;
    font-size: 12px;
}
.honda-download-input:focus {
    outline: none;
    border-color: var(--primary-color, #4488ff);
}

.honda-download-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 2px 4px;
    flex-shrink: 0;
}
.honda-download-btn:hover {
    opacity: 0.8;
}

.honda-download-progress-bar {
    height: 4px;
    background: rgba(255,255,255,0.1);
    border-radius: 2px;
    overflow: hidden;
    margin-top: 2px;
}
.honda-download-progress-fill {
    height: 100%;
    background: #4488ff;
    width: 0%;
    transition: width 0.1s linear;
}

.honda-download-add-btn {
    background: rgba(255,255,255,0.1);
    border: 1px dashed rgba(255,255,255,0.3);
    color: var(--fg-color);
    padding: 6px 10px;
    border-radius: 4px;
    cursor: pointer;
    text-align: center;
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    flex: 1 1 130px;
    min-width: 0;
    box-sizing: border-box;
}
.honda-download-add-btn:hover {
    background: rgba(255,255,255,0.2);
}

.honda-download-all-btn {
    background: var(--primary-color, #4488ff);
    color: white;
    border: none;
    padding: 8px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    flex: 1 1 130px;
    min-width: 0;
    box-sizing: border-box;
}
.honda-download-all-btn:hover {
    filter: brightness(1.1);
}

.honda-download-bottom-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 4px;
    overflow: hidden;
}
`;

function attachResizeToNode(node, container, domWidget, minH = 150) {
    const TITLE_H   = LiteGraph?.NODE_TITLE_HEIGHT ?? 30;
    const WIDGET_H  = LiteGraph?.NODE_WIDGET_HEIGHT ?? 20;
    const PADDING   = 16;

    let currentH = parseInt(container.style.height) || minH;

    const computeH = (size) => {
        const othersH = (node.widgets || []).reduce((sum, w) => {
            if (w === domWidget || w.hidden) return sum;
            if (typeof w.computeSize === "function") {
                const ws = w.computeSize(size[0]);
                return sum + (Array.isArray(ws) ? ws[1] : (typeof ws === "number" ? ws : WIDGET_H));
            }
            return sum + WIDGET_H;
        }, 0);
        return Math.max(minH, size[1] - TITLE_H - othersH - PADDING);
    };

    const origOnResize = node.onResize;
    node.onResize = function(size) {
        origOnResize?.call(this, size);
        const newH = computeH(size);
        if (newH !== currentH) {
            currentH = newH;
            container.style.height = newH + "px";
        }
    };

    return { getMinHeight: () => currentH };
}

app.registerExtension({
    name: "HondaNodes.DownloadFiles",
    
    setup() {
        // Listen to websocket messages for progress
        api.addEventListener("honda_download_progress", (e) => {
            const data = e.detail;
            const event = new CustomEvent("honda_download_update", { detail: data });
            window.dispatchEvent(event);
        });
    },

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "Honda_DownloadFiles") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);

                const node = this;
                
                const configWidget = node.widgets?.find(w => w.name === "downloads_config");
                if (configWidget) {
                    configWidget.hidden = true;
                    configWidget.computeSize = () => [0, -4];
                }

                let downloads = [];
                try {
                    downloads = JSON.parse(configWidget?.value || "[]");
                } catch (e) {}
                
                if (downloads.length === 0) {
                    downloads.push({ dir: "models/checkpoints", url: "" });
                }

                const container = document.createElement("div");
                container.className = "honda-download-widget";
                container.style.height = "200px";

                const style = document.createElement("style");
                style.textContent = DOWNLOAD_STYLE;
                container.appendChild(style);

                const listContainer = document.createElement("div");
                listContainer.style.display = "flex";
                listContainer.style.flexDirection = "column";
                listContainer.style.gap = "8px";

                // Persistent event delegation — survives innerHTML rebuilds inside listContainer.
                // Per-item buttons set data-action and data-index; we handle them here.
                // We use 'mousedown' instead of 'click' because rapid WebSocket updates 
                // can rebuild the DOM between mousedown and mouseup, preventing 'click' from firing.
                listContainer.addEventListener("mousedown", async (e) => {
                    const btn = e.target.closest("[data-action]");
                    if (!btn) return;
                    // Prevent default to stop inputs from losing focus unnecessarily
                    e.preventDefault();
                    
                    const index = parseInt(btn.dataset.index, 10);
                    if (isNaN(index)) return;
                    const item = downloads[index];
                    if (!item) return;
                    const action = btn.dataset.action;

                    if (action === "toggle") {
                        if (item.status === "canceling") return;
                        if (item.status === "downloading") {
                            item.status = "canceling";
                            updateUI();
                            try {
                                await api.fetchApi("/honda/tools/download/cancel", {
                                    method: "POST",
                                    body: JSON.stringify({ url: item.url })
                                });
                            } catch (_) {}
                        } else {
                            if (!item.url || !item.dir) return;
                            if (item.isDuplicate) {
                                alert("Cannot download duplicate files. Please remove or fix the duplicated entry.");
                                return;
                            }
                            if (item.status === "done" && !confirm("This file is already downloaded. Are you sure you want to download it again?")) return;
                            item.status = "downloading";
                            item.progress = 0;
                            updateUI();
                            try {
                                await api.fetchApi("/honda/tools/download", {
                                    method: "POST",
                                    body: JSON.stringify({ url: item.url, directory: item.dir })
                                });
                            } catch (_) {
                                item.status = "error";
                                updateUI();
                            }
                        }
                    } else if (action === "delete") {
                        if (item.dir || item.url) {
                            if (!confirm("Are you sure you want to remove this download?")) return;
                        }
                        downloads.splice(index, 1);
                        saveConfig();
                        updateUI();
                    }
                });


                const addBtn = document.createElement("div");
                addBtn.className = "honda-download-add-btn";
                addBtn.textContent = "➕ Add File";
                
                const downloadAllBtn = document.createElement("button");
                downloadAllBtn.className = "honda-download-all-btn";
                downloadAllBtn.textContent = "📥 Download All";

                const bottomBar = document.createElement("div");
                bottomBar.className = "honda-download-bottom-bar";
                bottomBar.appendChild(addBtn);
                bottomBar.appendChild(downloadAllBtn);
                
                container.appendChild(listContainer);
                container.appendChild(bottomBar);

                const saveConfig = () => {
                    if (configWidget) configWidget.value = JSON.stringify(downloads);
                    app.graph.setDirtyCanvas(true, true);
                };

                    const getFilename = (url) => {
                        if (!url) return "";
                        try {
                            const p = new URL(url).pathname;
                            return p.split("/").filter(Boolean).pop() || url;
                        } catch {
                            return url.split("/").filter(Boolean).pop() || url;
                        }
                    };

                    // Throttle websocket-driven redraws to one per animation frame.
                    // User-interaction calls updateUI() directly for instant feedback.
                    let _rafPending = false;
                    const scheduleUpdate = () => {
                        if (!_rafPending) {
                            _rafPending = true;
                            requestAnimationFrame(() => {
                                _rafPending = false;
                                updateUI();
                            });
                        }
                    };

                    const updateUI = () => {
                        listContainer.innerHTML = "";
                        let allDownloaded = true;
                        let anyDownloading = false;
                        let anyCanceling = false;
                        let anyValid = false;
                        
                        // Detect duplicates
                        const seen = {};
                        downloads.forEach(item => item.isDuplicate = false);
                        downloads.forEach((item, index) => {
                            if (!item.url || !item.dir) return;
                            const filename = getFilename(item.url);
                            const pathKey = (item.dir.replace(/\\/g, "/").replace(/\/$/, "") + "/" + filename).toLowerCase();
                            if (seen[pathKey] !== undefined) {
                                item.isDuplicate = true;
                                downloads[seen[pathKey]].isDuplicate = true;
                            } else {
                                seen[pathKey] = index;
                            }
                        });

                        downloads.forEach((item, index) => {
                            if (item.status === "downloading") anyDownloading = true;
                            if (item.status === "canceling") anyCanceling = true;
                            if (item.status !== "done") allDownloaded = false;
                            if (item.url && item.dir && !item.isDuplicate) anyValid = true;

                            const row = document.createElement("div");
                            row.className = "honda-download-row";
                            if (item.isDuplicate) {
                                row.style.borderColor = "#ff9800";
                            }

                            
                            const inputsRow = document.createElement("div");
                            inputsRow.className = "honda-download-row-inputs";
                            
                            const dirInput = document.createElement("input");
                            dirInput.className = "honda-download-input";
                            dirInput.placeholder = "Directory (e.g. models/checkpoints)";
                            dirInput.value = item.dir || "";
                            dirInput.onchange = (e) => { 
                                item.dir = e.target.value; 
                                saveConfig(); 
                                scheduleUpdate();
                                if (node._hondaCheckFilesExist) node._hondaCheckFilesExist(); 
                            };
                            
                            const urlInput = document.createElement("input");
                            urlInput.className = "honda-download-input";
                            urlInput.placeholder = "URL";
                            
                            if (item.urlValid === false) {
                                urlInput.style.color = "#ff5555";
                                urlInput.title = "URL might be invalid or unreachable";
                                urlInput.style.borderColor = "#ff5555";
                            }
                            
                            // When blurred: show only filename; when focused: show full URL
                            urlInput.value = item.url ? getFilename(item.url) : "";
                            
                            urlInput.addEventListener("focus", () => {
                                urlInput.value = item.url || "";
                            });
                            
                            urlInput.addEventListener("keydown", (e) => {
                                if (e.key === "Enter") {
                                    urlInput.blur();
                                }
                            });
                            
                            urlInput.addEventListener("blur", async (e) => {
                                const newUrl = e.target.value.trim();
                                const changed = (item.url !== newUrl);
                                item.url = newUrl;
                                
                                saveConfig();
                                scheduleUpdate();
                                urlInput.value = item.url ? getFilename(item.url) : "";
                                if (node._hondaCheckFilesExist) node._hondaCheckFilesExist();
                                
                                if (changed && item.url) {
                                    item.lastCheckedUrl = item.url;
                                    urlInput.style.opacity = "0.5";
                                    try {
                                        const res = await api.fetchApi("/honda/tools/download/check_url", {
                                            method: "POST",
                                            body: JSON.stringify({ url: item.url })
                                        });
                                        const data = await res.json();
                                        if (item.url === item.lastCheckedUrl) {
                                            item.urlValid = data.valid;
                                            scheduleUpdate();
                                        }
                                    } catch (err) {
                                        // Ignore fetch errors to not spam console
                                    } finally {
                                        urlInput.style.opacity = "1";
                                    }
                                }
                            });
                            
                            const btn = document.createElement("button");
                            btn.className = "honda-download-btn";
                            btn.dataset.action = "toggle";
                            btn.dataset.index = index;
                            
                            if (item.status === "canceling") {
                                btn.textContent = "⏳";
                                btn.title = "Canceling...";
                                btn.disabled = true;
                                btn.style.opacity = "0.4";
                                btn.style.cursor = "not-allowed";
                            } else if (item.status === "downloading") {
                                btn.textContent = "⏹️";
                                btn.title = "Cancel download";
                            } else if (item.status === "done") {
                                btn.textContent = "✔️";
                                btn.title = "Redownload";
                            } else {
                                btn.textContent = "⬇️";
                                btn.title = "Download";
                                if (!item.url || !item.dir) {
                                    btn.style.filter = "grayscale(100%)";
                                    btn.style.cursor = "not-allowed";
                                } else if (item.isDuplicate) {
                                    btn.textContent = "⚠️";
                                    btn.title = "Duplicate file path. Please change URL or directory.";
                                    btn.style.filter = "grayscale(100%)";
                                    btn.style.cursor = "not-allowed";
                                }
                            }
                            
                            const delBtn = document.createElement("button");
                            delBtn.className = "honda-download-btn";
                            delBtn.textContent = "🗑️";
                            delBtn.title = "Remove";
                            delBtn.dataset.action = "delete";
                            delBtn.dataset.index = index;
                            
                            const topRow = document.createElement("div");
                            topRow.className = "honda-download-row-top";

                            const btnGroup = document.createElement("div");
                            btnGroup.className = "honda-download-btn-group";

                            btnGroup.appendChild(btn);
                            btnGroup.appendChild(delBtn);

                            // Layout: Directory and buttons on top
                            topRow.appendChild(dirInput);
                            topRow.appendChild(btnGroup);

                            // URL on bottom line
                            inputsRow.appendChild(topRow);
                            inputsRow.appendChild(urlInput);
                            
                            const progressContainer = document.createElement("div");
                            progressContainer.className = "honda-download-progress-bar";
                            const progressFill = document.createElement("div");
                            progressFill.className = "honda-download-progress-fill";
                            progressFill.style.width = (item.progress || 0) + "%";
                            
                            if (item.status === "error") {
                                progressFill.style.background = "red";
                                progressFill.style.width = "100%";
                            } else if (item.status === "done") {
                                progressFill.style.background = "#4caf50";
                                progressFill.style.width = "100%";
                                row.style.borderColor = "#4caf50";
                            } else if (item.status === "canceling") {
                                progressFill.style.background = "#ff9800";
                            }
                            
                            progressContainer.appendChild(progressFill);
                            row.appendChild(inputsRow);
                            row.appendChild(progressContainer);
                            listContainer.appendChild(row);
                        });
                        
                        if (anyCanceling) {
                            downloadAllBtn.textContent = "⏳ Canceling...";
                            downloadAllBtn.style.background = "#888";
                            downloadAllBtn.style.filter = "";
                            downloadAllBtn.disabled = true;
                            downloadAllBtn.style.cursor = "not-allowed";
                            downloadAllBtn.onclick = null;
                        } else if (anyDownloading) {
                            downloadAllBtn.textContent = "Cancel All Downloads";
                            downloadAllBtn.style.background = "#f44336";
                            downloadAllBtn.style.filter = "";
                            downloadAllBtn.disabled = false;
                            downloadAllBtn.style.cursor = "pointer";
                            downloadAllBtn.onclick = async () => {
                                // Mark all downloading items as canceling at once
                                const toCancel = downloads.filter(item => item.status === "downloading");
                                toCancel.forEach(item => { item.status = "canceling"; });
                                updateUI();
                                // Fire all cancel requests in parallel
                                await Promise.all(toCancel.map(item =>
                                    api.fetchApi("/honda/tools/download/cancel", {
                                        method: "POST",
                                        body: JSON.stringify({ url: item.url })
                                    }).catch(() => {})
                                ));
                            };
                        } else if (downloads.length > 0 && allDownloaded) {
                            downloadAllBtn.textContent = "All Files Downloaded";
                            downloadAllBtn.style.background = "#4caf50";
                            downloadAllBtn.style.filter = "";
                            downloadAllBtn.disabled = false;
                            downloadAllBtn.style.cursor = "pointer";
                            downloadAllBtn.onclick = () => {
                                if (confirm("All files are already downloaded. Are you sure you want to force re-download all of them?")) {
                                    startDownloadAll(true);
                                }
                            };
                        } else {
                            downloadAllBtn.textContent = "Download All Files";
                            downloadAllBtn.style.background = "var(--primary-color, #4488ff)";
                            downloadAllBtn.style.cursor = anyValid ? "pointer" : "not-allowed";
                            downloadAllBtn.style.filter = anyValid ? "" : "grayscale(100%)";
                            downloadAllBtn.disabled = false;
                            downloadAllBtn.onclick = () => startDownloadAll(false);
                        }
                    };
                    
                    const startDownloadAll = async (force = false) => {
                        for (const item of downloads) {
                            if (!item.url || !item.dir || item.isDuplicate) continue;
                            if (item.status === "canceling") continue; // never overwrite a canceling item
                            if (item.status === "done" && !force) continue;
                            
                            item.status = "downloading";
                            item.progress = 0;
                            updateUI();
                            try {
                                await api.fetchApi("/honda/tools/download", {
                                    method: "POST",
                                    body: JSON.stringify({ url: item.url, directory: item.dir })
                                });
                            } catch (e) {
                                item.status = "error";
                                updateUI();
                            }
                        }
                    };
                    
                    addBtn.onclick = () => {
                        downloads.push({ dir: "", url: "", status: "idle", progress: 0 });
                        saveConfig();
                        updateUI();
                    };

                // Listen to global updates
                window.addEventListener("honda_download_update", (e) => {
                    const data = e.detail;
                    const item = downloads.find(d => d.url === data.url);
                    if (item) {
                        // While canceling, ignore all backend progress updates — only
                        // accept the final "idle" or "error" confirmation to unblock the UI.
                        if (item.status === "canceling" && data.status === "downloading") return;
                        item.progress = data.progress;
                        item.status = data.status;
                        if (data.status === "error") {
                            console.error("[Honda Download]", data.error);
                        }
                        // Throttled: prevents rapid DOM teardown from making buttons unclickable
                        scheduleUpdate();
                    }
                });

                const checkFilesExist = async () => {
                    if (downloads.length === 0) return;
                    try {
                        const payload = downloads.map(d => ({ url: d.url, dir: d.dir }));
                        const resp = await api.fetchApi("/honda/tools/download/check", {
                            method: "POST",
                            body: JSON.stringify(payload)
                        });
                        const data = await resp.json();
                        if (data.results) {
                            let changed = false;
                            downloads.forEach(d => {
                                if (data.results[d.url]) {
                                    if (d.status !== "done") {
                                        d.status = "done";
                                        d.progress = 100;
                                        changed = true;
                                    }
                                } else {
                                    if (d.status === "done") {
                                        d.status = "idle";
                                        d.progress = 0;
                                        changed = true;
                                    }
                                }
                            });
                            if (changed) {
                                saveConfig();
                                updateUI();
                            }
                        }
                    } catch (e) {}
                };
                
                node._hondaCheckFilesExist = checkFilesExist;

                updateUI();
                checkFilesExist();

                const domWidget = node.addDOMWidget("honda_download_widget", "div", container, {
                    getValue: () => configWidget?.value ?? "[]",
                    setValue: (v) => { 
                        if (configWidget) configWidget.value = v; 
                        try { downloads = JSON.parse(v || "[]"); updateUI(); checkFilesExist(); } catch(e){}
                    },
                    getMinHeight: () => resizer.getMinHeight(),
                    hideOnZoom: false,
                });

                const resizer = attachResizeToNode(node, container, domWidget, 200);
            };

            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                if (onConfigure) onConfigure.apply(this, arguments);
                if (this._hondaCheckFilesExist) {
                    this._hondaCheckFilesExist();
                }
            };
        }
    }
});
