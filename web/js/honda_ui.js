import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const HONDA_STYLE = `
.honda-upload-widget {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    padding: 6px 8px;
    gap: 4px;
}

/* State: no image loaded */
.honda-dropzone {
    border: 2px dashed #666;
    border-radius: 6px;
    flex: 1;
    min-height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #aaa;
    font-size: 13px;
    transition: border-color 0.15s, color 0.15s;
    user-select: none;
    box-sizing: border-box;
}

.honda-dropzone:hover,
.honda-dropzone.drag-over {
    border-color: #bbb;
    color: #eee;
}

.honda-preview-wrap {
    position: relative;
    cursor: pointer;
    border-radius: 4px;
    overflow: hidden;
    display: none;
    flex-direction: column;
    flex: 1;
    min-height: 0;
}

.honda-preview-wrap.visible {
    display: flex;
}

.honda-img-container {
    flex: 1;
    position: relative;
    min-height: 0;
    width: 100%;
}

.honda-img-container img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
    border-radius: 4px;
}


.honda-preview-wrap .honda-overlay {
    position: absolute;
    inset: 0;
    background: transparent;
    transition: background 0.15s;
    pointer-events: none;
}

.honda-preview-wrap:hover .honda-overlay,
.honda-preview-wrap.drag-over .honda-overlay {
    background: rgba(0,0,0,0.25);
}

.honda-filename {
    color: #888;
    font-size: 11px;
    line-height: 1.4;
    word-break: break-all;
    white-space: normal;
    padding: 0;
    pointer-events: none;
    flex-shrink: 0;
    text-align: center;
}

.honda-clear-btn {
    position: absolute;
    top: 6px;
    right: 6px;
    background: rgba(0,0,0,0.6);
    color: white;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    cursor: pointer;
    display: none;
    z-index: 10;
    transition: background 0.15s;
}

.honda-preview-wrap:hover .honda-clear-btn {
    display: block;
}

.honda-clear-btn:hover {
    background: rgba(220, 50, 50, 0.9);
}

/* Save Image Grid Specific */
.honda-save-grid {
    display: none;
    grid-template-columns: 1fr;
    gap: 8px;
    flex: 1;
    min-height: 0;
    width: 100%;
    align-items: stretch;
}
.honda-save-grid.visible {
    display: grid;
}
.honda-save-grid-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow: hidden;
    min-height: 0;
}
`;

/**
 * Shared helper: ties a DOM container's height to the node's actual height.
 * The container fills the remaining vertical space after accounting for the
 * title bar and all standard (non-DOM) widgets. The height NEVER grows due
 * to image content — only due to the user manually resizing the node.
 *
 * @param {object} node        - LiteGraph node instance
 * @param {HTMLElement} container - the container element to resize
 * @param {object} domWidget   - the widget returned by addDOMWidget (to skip it)
 * @param {number} minH        - minimum container height in px
 * @returns {{ getMinHeight: () => number }}
 */
function attachResizeToNode(node, container, domWidget, minH = 80) {
    const TITLE_H   = LiteGraph?.NODE_TITLE_HEIGHT ?? 30;
    const WIDGET_H  = LiteGraph?.NODE_WIDGET_HEIGHT ?? 20;
    const PADDING   = 16;

    let currentH = parseInt(container.style.height) || 250;

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
    name: "HondaNodes.UI",

    async beforeRegisterNodeDef(nodeType, nodeData) {

        // ── Load Image ────────────────────────────────────────────────────────
        if (nodeData.name === "Honda_LoadImage") {

            if (!document.getElementById("honda-nodes-style")) {
                const style = document.createElement("style");
                style.id = "honda-nodes-style";
                style.textContent = HONDA_STYLE;
                document.head.appendChild(style);
            }

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);

                const node = this;

                // Hide the raw image_file string widget — keep it for serialisation
                const fileWidget = node.widgets?.find(w => w.name === "image_file");
                if (fileWidget) {
                    fileWidget.hidden = true;
                    fileWidget.computeSize = () => [0, -4];
                }

                // ── Build DOM ────────────────────────────────────────────────
                const container = document.createElement("div");
                container.className = "honda-upload-widget";
                container.style.height = "120px"; // initial — overwritten by onResize

                const dropzone = document.createElement("div");
                dropzone.className = "honda-dropzone";
                dropzone.textContent = "📂 Click or Drop Image Here";

                const previewWrap = document.createElement("div");
                previewWrap.className = "honda-preview-wrap";

                const imgContainer = document.createElement("div");
                imgContainer.className = "honda-img-container";

                const previewImg = document.createElement("img");
                previewImg.alt = "";

                imgContainer.appendChild(previewImg);

                const overlay = document.createElement("div");
                overlay.className = "honda-overlay";

                const filenameEl = document.createElement("div");
                filenameEl.className = "honda-filename";

                const clearBtn = document.createElement("button");
                clearBtn.className = "honda-clear-btn";
                clearBtn.textContent = "Clear";
                clearBtn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    if (fileWidget) fileWidget.value = "";
                    showState("");
                });

                previewWrap.appendChild(imgContainer);
                previewWrap.appendChild(overlay);
                previewWrap.appendChild(filenameEl);
                previewWrap.appendChild(clearBtn);

                container.appendChild(dropzone);
                container.appendChild(previewWrap);

                // ── State helpers ────────────────────────────────────────────
                const showState = (filename) => {
                    if (filename) {
                        dropzone.style.display = "none";
                        previewWrap.classList.add("visible");
                        filenameEl.textContent = filename;
                        previewImg.src = api.apiURL(
                            `/view?filename=${encodeURIComponent(filename)}&type=input&t=${Date.now()}`
                        );
                    } else {
                        dropzone.style.display = "";
                        previewWrap.classList.remove("visible");
                        previewImg.src = "";
                        filenameEl.textContent = "";
                    }
                    app.graph.setDirtyCanvas(true, true);
                };

                const openFilePicker = () => {
                    const input = document.createElement("input");
                    input.type = "file";
                    input.accept = "image/*";
                    input.onchange = (e) => {
                        const f = e.target.files[0];
                        if (f) doUpload(f);
                    };
                    input.click();
                };

                const doUpload = async (file) => {
                    const body = new FormData();
                    body.append("image", file);
                    body.append("type", "input");
                    try {
                        const resp = await api.fetchApi("/upload/image", { method: "POST", body });
                        const data = await resp.json();
                        if (data.name) {
                            if (fileWidget) fileWidget.value = data.name;
                            showState(data.name);
                        }
                    } catch (e) {
                        console.error("[Honda Nodes] Upload failed", e);
                    }
                };

                // ── Events: dropzone ─────────────────────────────────────────
                dropzone.addEventListener("click", openFilePicker);
                dropzone.addEventListener("dragover", (e) => { e.preventDefault(); dropzone.classList.add("drag-over"); });
                dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
                dropzone.addEventListener("drop", (e) => {
                    e.preventDefault();
                    dropzone.classList.remove("drag-over");
                    const f = e.dataTransfer?.files[0];
                    if (f?.type.startsWith("image/")) doUpload(f);
                });

                // ── Events: preview wrap ─────────────────────────────────────
                previewWrap.addEventListener("click", openFilePicker);
                previewWrap.addEventListener("dragover", (e) => { e.preventDefault(); previewWrap.classList.add("drag-over"); });
                previewWrap.addEventListener("dragleave", () => previewWrap.classList.remove("drag-over"));
                previewWrap.addEventListener("drop", (e) => {
                    e.preventDefault();
                    previewWrap.classList.remove("drag-over");
                    const f = e.dataTransfer?.files[0];
                    if (f?.type.startsWith("image/")) doUpload(f);
                });

                // ── Canvas-level drop ────────────────────────────────────────
                node.onDropFile = function(file) {
                    if (file?.type.startsWith("image/")) { doUpload(file); return true; }
                    return false;
                };

                // ── Register DOM widget ──────────────────────────────────────
                const domWidget = node.addDOMWidget("honda_image_upload", "div", container, {
                    getValue: () => fileWidget?.value ?? "",
                    setValue: (v) => { if (fileWidget) fileWidget.value = v; showState(v); },
                    getMinHeight: () => resizer.getMinHeight(),
                    hideOnZoom: false,
                });

                const resizer = attachResizeToNode(node, container, domWidget, 80);

                node._hondaShowState = showState;

                api.addEventListener("executed", (e) => {
                    const detail = e.detail;
                    if (detail && detail.node == node.id) {
                        const output = detail.output;
                        if (output?.honda_preview?.[0]?.filename && node._hondaShowState) {
                            node._hondaShowState(output.honda_preview[0].filename);
                        }
                    }
                });
            };

            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                if (onConfigure) onConfigure.apply(this, arguments);
                const fileWidget = this.widgets?.find(w => w.name === "image_file");
                if (fileWidget?.value && this._hondaShowState) {
                    requestAnimationFrame(() => this._hondaShowState(fileWidget.value));
                }
            };
        }

        // ── Preview Image ─────────────────────────────────────────────────────
        if (nodeData.name === "Honda_PreviewImage") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);

                const node = this;

                const container = document.createElement("div");
                container.className = "honda-upload-widget";
                container.style.height = "120px";

                const dropzone = document.createElement("div");
                dropzone.className = "honda-dropzone";
                dropzone.textContent = "Preview";

                const previewWrap = document.createElement("div");
                previewWrap.className = "honda-preview-wrap";

                const imgContainer = document.createElement("div");
                imgContainer.className = "honda-img-container";

                const previewImg = document.createElement("img");
                previewImg.alt = "";

                imgContainer.appendChild(previewImg);
                previewWrap.appendChild(imgContainer);
                container.appendChild(dropzone);
                container.appendChild(previewWrap);

                const domWidget = node.addDOMWidget("honda_preview_image_widget", "div", container, {
                    getValue: () => "",
                    setValue: () => {},
                    getMinHeight: () => resizer.getMinHeight(),
                    hideOnZoom: false,
                });

                const resizer = attachResizeToNode(node, container, domWidget, 80);

                api.addEventListener("executed", (e) => {
                    const detail = e.detail;
                    if (detail && detail.node == node.id) {
                        const files = detail.output?.honda_preview_image;
                        if (files?.length > 0) {
                            const first = files[0];
                            previewImg.src = api.apiURL(`/view?filename=${encodeURIComponent(first.filename)}&type=${first.type}&t=${Date.now()}`);
                            dropzone.style.display = "none";
                            previewWrap.classList.add("visible");
                        } else {
                            dropzone.style.display = "";
                            previewWrap.classList.remove("visible");
                            previewImg.src = "";
                        }
                    }
                });
            };
        }

        // ── Save Image ────────────────────────────────────────────────────────
        if (nodeData.name === "Honda_SaveImage") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);

                const node = this;

                const container = document.createElement("div");
                container.className = "honda-upload-widget";
                container.style.height = "120px";

                const dropzone = document.createElement("div");
                dropzone.className = "honda-dropzone";
                dropzone.textContent = "Preview";

                const saveGrid = document.createElement("div");
                saveGrid.className = "honda-save-grid";

                container.appendChild(dropzone);
                container.appendChild(saveGrid);

                const domWidget = node.addDOMWidget("honda_save_preview_widget", "div", container, {
                    getValue: () => "",
                    setValue: () => {},
                    getMinHeight: () => resizer.getMinHeight(),
                });

                const resizer = attachResizeToNode(node, container, domWidget, 80);

                node._hondaUpdateSavePreview = (previews) => {
                    saveGrid.innerHTML = "";
                    if (!previews || previews.length === 0) {
                        dropzone.style.display = "";
                        saveGrid.classList.remove("visible");
                        return;
                    }
                    
                    const validPreviews = previews.filter(p => p);
                    if (validPreviews.length === 0) {
                        dropzone.style.display = "";
                        saveGrid.classList.remove("visible");
                        return;
                    }

                    dropzone.style.display = "none";
                    saveGrid.classList.add("visible");
                    
                    saveGrid.style.gridTemplateColumns = `repeat(${validPreviews.length}, minmax(0, 1fr))`;

                    validPreviews.forEach(p => {
                        const item = document.createElement("div");
                        item.className = "honda-save-grid-item";

                        const imgContainer = document.createElement("div");
                        imgContainer.className = "honda-img-container";

                        const img = document.createElement("img");
                        img.src = api.apiURL(`/view?filename=${encodeURIComponent(p.filename)}&type=${p.type}&t=${Date.now()}`);

                        imgContainer.appendChild(img);

                        const label = document.createElement("div");
                        label.className = "honda-filename";
                        label.textContent = p.format || "Preview";

                        item.appendChild(imgContainer);
                        item.appendChild(label);
                        saveGrid.appendChild(item);
                    });
                };

                api.addEventListener("executed", (e) => {
                    const detail = e.detail;
                    if (detail && detail.node == node.id) {
                        const output = detail.output;
                        if (output?.honda_save_preview && node._hondaUpdateSavePreview) {
                            node._hondaUpdateSavePreview(output.honda_save_preview);
                        }
                    }
                });
            };
        }
    }
});
