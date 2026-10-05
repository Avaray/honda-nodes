import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const DOWNLOAD_STYLE = `
.honda-download-widget {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px;
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
    gap: 4px;
    align-items: center;
}

.honda-download-input {
    flex: 1;
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
    transition: transform 0.1s;
}
.honda-download-btn:hover {
    transform: scale(1.1);
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
    padding: 6px;
    border-radius: 4px;
    cursor: pointer;
    text-align: center;
    font-size: 12px;
}
.honda-download-add-btn:hover {
    background: rgba(255,255,255,0.2);
}

.honda-download-all-btn {
    background: var(--primary-color, #4488ff);
    color: white;
    border: none;
    padding: 8px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    text-align: center;
    margin-top: 4px;
}
.honda-download-all-btn:hover {
    filter: brightness(1.1);
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
                
                const addBtn = document.createElement("div");
                addBtn.className = "honda-download-add-btn";
                addBtn.textContent = "➕ Add File";
                
                const downloadAllBtn = document.createElement("button");
                downloadAllBtn.className = "honda-download-all-btn";
                downloadAllBtn.textContent = "📥 Download All";
                
                container.appendChild(listContainer);
                container.appendChild(addBtn);
                container.appendChild(downloadAllBtn);

                const saveConfig = () => {
                    if (configWidget) configWidget.value = JSON.stringify(downloads);
                    app.graph.setDirtyCanvas(true, true);
                };

                const updateUI = () => {
                    listContainer.innerHTML = "";
                    let allDownloaded = true;
                    
                    downloads.forEach((item, index) => {
                        const row = document.createElement("div");
                        row.className = "honda-download-row";
                        
                        const inputsRow = document.createElement("div");
                        inputsRow.className = "honda-download-row-inputs";
                        
                        const dirInput = document.createElement("input");
                        dirInput.className = "honda-download-input";
                        dirInput.placeholder = "Directory (e.g. models/checkpoints)";
                        dirInput.value = item.dir || "";
                        dirInput.onchange = (e) => { item.dir = e.target.value; saveConfig(); };
                        
                        const urlInput = document.createElement("input");
                        urlInput.className = "honda-download-input";
                        urlInput.placeholder = "URL";
                        urlInput.value = item.url || "";
                        urlInput.onchange = (e) => { item.url = e.target.value; saveConfig(); };
                        
                        const btn = document.createElement("button");
                        btn.className = "honda-download-btn";
                        btn.textContent = item.status === "done" ? "✅" : "📥";
                        btn.title = "Download this file";
                        
                        const delBtn = document.createElement("button");
                        delBtn.className = "honda-download-btn";
                        delBtn.textContent = "❌";
                        delBtn.title = "Remove";
                        delBtn.onclick = () => {
                            downloads.splice(index, 1);
                            saveConfig();
                            updateUI();
                        };
                        
                        inputsRow.appendChild(dirInput);
                        inputsRow.appendChild(urlInput);
                        inputsRow.appendChild(btn);
                        inputsRow.appendChild(delBtn);
                        
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
                        }
                        
                        progressContainer.appendChild(progressFill);
                        row.appendChild(inputsRow);
                        row.appendChild(progressContainer);
                        listContainer.appendChild(row);
                        
                        if (item.status !== "done") allDownloaded = false;
                        
                        // Handle single download
                        btn.onclick = async () => {
                            if (!item.url || !item.dir) return;
                            item.status = "downloading";
                            item.progress = 0;
                            btn.textContent = "⏳";
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
                        };
                    });
                    
                    if (downloads.length > 0 && allDownloaded) {
                        downloadAllBtn.textContent = "✅ All Files Downloaded (Click to Force)";
                        downloadAllBtn.style.background = "#4caf50";
                    } else {
                        downloadAllBtn.textContent = "📥 Download All";
                        downloadAllBtn.style.background = "var(--primary-color, #4488ff)";
                    }
                };
                
                addBtn.onclick = () => {
                    downloads.push({ dir: "models/checkpoints", url: "", status: "idle", progress: 0 });
                    saveConfig();
                    updateUI();
                };
                
                downloadAllBtn.onclick = async () => {
                    for (const item of downloads) {
                        if (!item.url || !item.dir) continue;
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

                // Listen to global updates
                window.addEventListener("honda_download_update", (e) => {
                    const data = e.detail;
                    const item = downloads.find(d => d.url === data.url);
                    if (item) {
                        item.progress = data.progress;
                        item.status = data.status;
                        if (data.status === "error") {
                            console.error("[Honda Download]", data.error);
                        }
                        updateUI();
                    }
                });

                updateUI();

                const domWidget = node.addDOMWidget("honda_download_widget", "div", container, {
                    getValue: () => configWidget?.value ?? "[]",
                    setValue: (v) => { 
                        if (configWidget) configWidget.value = v; 
                        try { downloads = JSON.parse(v || "[]"); updateUI(); } catch(e){}
                    },
                    getMinHeight: () => resizer.getMinHeight(),
                    hideOnZoom: false,
                });

                const resizer = attachResizeToNode(node, container, domWidget, 200);
            };
        }
    }
});
