import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const PREVIEW_STYLE = `
.honda-load-image-widget {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 6px 8px;
    box-sizing: border-box;
    width: 100%;
}

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
    transition: border-color 0.2s, color 0.2s;
    user-select: none;
}

.honda-dropzone:hover,
.honda-dropzone.drag-over {
    border-color: #999;
    color: #ccc;
}

.honda-filename {
    color: #888;
    font-size: 11px;
    line-height: 1.4;
    word-break: break-all;
    white-space: normal;
    padding: 2px 0;
    min-height: 0;
    pointer-events: none;
    display: none;
}

.honda-filename.visible {
    display: block;
}

.honda-preview-img {
    width: 100%;
    height: auto;
    display: none;
    border-radius: 4px;
}

.honda-preview-img.visible {
    display: block;
}
`;

app.registerExtension({
    name: "HondaNodes.UI",

    async beforeRegisterNodeDef(nodeType, nodeData) {

        // ====================================================================
        // Honda_LoadImage: Custom DOM-based Drag & Drop Image Uploader
        // ====================================================================
        if (nodeData.name === "Honda_LoadImage") {

            // Inject CSS once
            if (!document.getElementById("honda-nodes-style")) {
                const style = document.createElement("style");
                style.id = "honda-nodes-style";
                style.textContent = PREVIEW_STYLE;
                document.head.appendChild(style);
            }

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);

                const node = this;

                // 1. Find and hide the raw image_file string widget
                const fileWidget = node.widgets?.find(w => w.name === "image_file");
                if (fileWidget) {
                    fileWidget.type = "hidden";
                    if (fileWidget.element) fileWidget.element.style.display = "none";
                }

                // 2. Build the DOM widget container
                const container = document.createElement("div");
                container.className = "honda-load-image-widget";

                // Drag & Drop Zone
                const dropzone = document.createElement("div");
                dropzone.className = "honda-dropzone";
                dropzone.textContent = "📂 Click or Drop Image Here";

                // File name display (always visible, no editing)
                const filenameEl = document.createElement("div");
                filenameEl.className = "honda-filename";

                // Preview image
                const previewImg = document.createElement("img");
                previewImg.className = "honda-preview-img";

                container.appendChild(dropzone);
                container.appendChild(filenameEl);
                container.appendChild(previewImg);

                // 3. Wire up click-to-upload
                dropzone.addEventListener("click", () => {
                    const fileInput = document.createElement("input");
                    fileInput.type = "file";
                    fileInput.accept = "image/*";
                    fileInput.onchange = (e) => {
                        const file = e.target.files[0];
                        if (file) doUpload(file);
                    };
                    fileInput.click();
                });

                // 4. Wire up drag and drop
                dropzone.addEventListener("dragover", (e) => {
                    e.preventDefault();
                    dropzone.classList.add("drag-over");
                });
                dropzone.addEventListener("dragleave", () => {
                    dropzone.classList.remove("drag-over");
                });
                dropzone.addEventListener("drop", (e) => {
                    e.preventDefault();
                    dropzone.classList.remove("drag-over");
                    const file = e.dataTransfer?.files[0];
                    if (file && file.type.startsWith("image/")) {
                        doUpload(file);
                    }
                });

                // 5. Also hook LiteGraph's canvas-level drop (files dragged onto canvas)
                node.onDropFile = function(file) {
                    if (file && file.type.startsWith("image/")) {
                        doUpload(file);
                        return true;
                    }
                    return false;
                };

                // 6. Load/refresh the preview
                const setPreview = (filename) => {
                    const previewOn = node.widgets?.find(w => w.name === "preview_image")?.value !== false;

                    // Always show filename
                    if (filename) {
                        filenameEl.textContent = filename;
                        filenameEl.classList.add("visible");
                    } else {
                        filenameEl.classList.remove("visible");
                    }

                    // Conditionally show image
                    if (filename && previewOn) {
                        previewImg.src = api.apiURL(`/view?filename=${encodeURIComponent(filename)}&type=input&t=${Date.now()}`);
                        previewImg.classList.add("visible");
                    } else {
                        previewImg.classList.remove("visible");
                        previewImg.src = "";
                    }

                    app.graph.setDirtyCanvas(true, true);
                };

                // 7. Upload helper
                const doUpload = async (file) => {
                    const body = new FormData();
                    body.append("image", file);
                    body.append("type", "input");
                    try {
                        const resp = await api.fetchApi("/upload/image", { method: "POST", body });
                        const data = await resp.json();
                        if (data.name) {
                            if (fileWidget) fileWidget.value = data.name;
                            setPreview(data.name);
                        }
                    } catch (e) {
                        console.error("[Honda Nodes] Upload failed", e);
                    }
                };

                // 8. Hook preview_image toggle
                const previewWidget = node.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        const currentFile = fileWidget?.value;
                        setPreview(currentFile);
                    };
                }

                // 9. Add the container as a DOM widget
                const domWidget = node.addDOMWidget("honda_image_upload", "div", container, {
                    getValue: () => fileWidget?.value ?? "",
                    setValue: (v) => {
                        if (fileWidget) fileWidget.value = v;
                        setPreview(v);
                    },
                    getMinHeight: () => 80,
                    hideOnZoom: false,
                });

                node._hondaSetPreview = setPreview;
            };

            // 10. When workflow is loaded from JSON, restore the preview
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                if (onConfigure) onConfigure.apply(this, arguments);
                const fileWidget = this.widgets?.find(w => w.name === "image_file");
                if (fileWidget?.value && this._hondaSetPreview) {
                    // Defer to next frame to allow widget render
                    requestAnimationFrame(() => this._hondaSetPreview(fileWidget.value));
                }
            };
        }

        // ====================================================================
        // Honda_SaveImage: Block preview when toggle is OFF
        // ====================================================================
        if (nodeData.name === "Honda_SaveImage") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                const node = this;

                let _realImgs = node.imgs;
                Object.defineProperty(node, "imgs", {
                    get() {
                        const pw = this.widgets?.find(w => w.name === "preview_image");
                        if (pw && !pw.value) return null;
                        return _realImgs;
                    },
                    set(val) { _realImgs = val; },
                    configurable: true
                });

                const previewWidget = node.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        if (!val) node.imgs = null;
                        app.graph.setDirtyCanvas(true, true);
                    };
                }
            };
        }
    }
});
