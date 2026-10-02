import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const HONDA_STYLE = `
.honda-upload-widget {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 6px 8px;
    box-sizing: border-box;
    width: 100%;
}

/* State: no image loaded */
.honda-dropzone {
    border: 2px dashed #666;
    border-radius: 6px;
    height: 70px;
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

/* State: image loaded — the preview IS the drop target */
.honda-preview-wrap {
    position: relative;
    cursor: pointer;
    border-radius: 4px;
    overflow: hidden;
    display: none;
    flex-direction: column;
    gap: 4px;
}

.honda-preview-wrap.visible {
    display: flex;
}

.honda-preview-wrap img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 4px;
}

.honda-preview-wrap .honda-overlay {
    position: absolute;
    inset: 0;
    background: transparent;
    transition: background 0.15s;
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
}
`;

app.registerExtension({
    name: "HondaNodes.UI",

    async beforeRegisterNodeDef(nodeType, nodeData) {

        if (nodeData.name === "Honda_LoadImage") {

            // Inject CSS once
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

                // Hide the raw image_file string widget — it must stay in
                // node.widgets for serialization (backend reads its value),
                // but setting hidden=true tells ComfyUI Vue not to render it.
                const fileWidget = node.widgets?.find(w => w.name === "image_file");
                if (fileWidget) {
                    fileWidget.hidden = true;
                    fileWidget.computeSize = () => [0, -4];
                }

                // ── Build DOM ────────────────────────────────────────────────
                const container = document.createElement("div");
                container.className = "honda-upload-widget";

                // Empty state: dashed zone
                const dropzone = document.createElement("div");
                dropzone.className = "honda-dropzone";
                dropzone.textContent = "📂 Click or Drop Image Here";

                // Loaded state: preview + overlay + filename
                const previewWrap = document.createElement("div");
                previewWrap.className = "honda-preview-wrap";

                const previewImg = document.createElement("img");
                previewImg.alt = "";

                const overlay = document.createElement("div");
                overlay.className = "honda-overlay";

                const filenameEl = document.createElement("div");
                filenameEl.className = "honda-filename";

                previewWrap.appendChild(previewImg);
                previewWrap.appendChild(overlay);
                previewWrap.appendChild(filenameEl);

                container.appendChild(dropzone);
                container.appendChild(previewWrap);

                // ── Shared helpers ───────────────────────────────────────────
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

                // ── Events on dropzone (empty state) ─────────────────────────
                dropzone.addEventListener("click", openFilePicker);

                dropzone.addEventListener("dragover", (e) => {
                    e.preventDefault();
                    dropzone.classList.add("drag-over");
                });
                dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
                dropzone.addEventListener("drop", (e) => {
                    e.preventDefault();
                    dropzone.classList.remove("drag-over");
                    const f = e.dataTransfer?.files[0];
                    if (f?.type.startsWith("image/")) doUpload(f);
                });

                // ── Events on preview (loaded state) ─────────────────────────
                previewWrap.addEventListener("click", openFilePicker);

                previewWrap.addEventListener("dragover", (e) => {
                    e.preventDefault();
                    previewWrap.classList.add("drag-over");
                });
                previewWrap.addEventListener("dragleave", () => previewWrap.classList.remove("drag-over"));
                previewWrap.addEventListener("drop", (e) => {
                    e.preventDefault();
                    previewWrap.classList.remove("drag-over");
                    const f = e.dataTransfer?.files[0];
                    if (f?.type.startsWith("image/")) doUpload(f);
                });

                // ── LiteGraph canvas-level drop ───────────────────────────────
                node.onDropFile = function(file) {
                    if (file?.type.startsWith("image/")) {
                        doUpload(file);
                        return true;
                    }
                    return false;
                };

                // ── Add as DOM widget ────────────────────────────────────────
                node.addDOMWidget("honda_image_upload", "div", container, {
                    getValue: () => fileWidget?.value ?? "",
                    setValue: (v) => {
                        if (fileWidget) fileWidget.value = v;
                        showState(v);
                    },
                    getMinHeight: () => 76,
                    hideOnZoom: false,
                });

                // Store showState so onConfigure can call it
                node._hondaShowState = showState;
            };

            // Restore preview when workflow loads
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                if (onConfigure) onConfigure.apply(this, arguments);
                const fileWidget = this.widgets?.find(w => w.name === "image_file");
                if (fileWidget?.value && this._hondaShowState) {
                    requestAnimationFrame(() => this._hondaShowState(fileWidget.value));
                }
            };

            // Catch execution result (e.g. from path_override) to update preview
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                if (onExecuted) onExecuted.apply(this, arguments);
                if (message?.honda_preview?.[0]?.filename && this._hondaShowState) {
                    this._hondaShowState(message.honda_preview[0].filename);
                }
            };
        }
    }
});
