import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
    name: "HondaNodes.UI",

    async beforeRegisterNodeDef(nodeType, nodeData) {

        // ====================================================================
        // Honda_LoadImage: Custom Drag & Drop Image Uploader
        // ====================================================================
        if (nodeData.name === "Honda_LoadImage") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                
                const node = this;

                // 1. Add Custom Upload Button Widget
                const uploadWidget = node.addWidget("button", "📂 Click or Drop Image", "upload", () => {
                    const fileInput = document.createElement("input");
                    fileInput.type = "file";
                    fileInput.accept = "image/*";
                    fileInput.onchange = (e) => {
                        const file = e.target.files[0];
                        if (file) uploadFile(node, file);
                    };
                    fileInput.click();
                });

                // 2. Add LiteGraph drag & drop handlers
                node.onDragOver = function(e) {
                    return true; 
                };

                node.onDragDrop = function(e) {
                    let handled = false;
                    if (e.dataTransfer && e.dataTransfer.files) {
                        const file = e.dataTransfer.files[0];
                        if (file && file.type.startsWith("image/")) {
                            uploadFile(node, file);
                            handled = true;
                        }
                    }
                    return handled;
                };

                // ComfyUI / LiteGraph sometimes uses this specific hook for canvas drops
                node.onDropFile = function(file) {
                    if (file && file.type.startsWith("image/")) {
                        uploadFile(node, file);
                        return true;
                    }
                    return false;
                };

                // 3. Custom Image Drawing (Bypassing ComfyUI Core)
                const instDraw = node.onDrawBackground;
                node.onDrawBackground = function (ctx) {
                    if (instDraw) instDraw.apply(this, arguments);
                    else if (nodeType.prototype.onDrawBackground) {
                        nodeType.prototype.onDrawBackground.apply(this, arguments);
                    }

                    // Only draw if preview is ON and we have images
                    const previewToggle = this.widgets?.find(w => w.name === "preview_image");
                    if (previewToggle && previewToggle.value && this.imgs && this.imgs.length > 0) {
                        const img = this.imgs[0];
                        if (img && img.complete && img.naturalWidth > 0) {
                            let widgetHeight = 0;
                            if (this.widgets) {
                                widgetHeight = this.widgets.reduce((sum, w) => sum + (w.computeSize ? w.computeSize()[1] : 20) + 4, 0);
                            }
                            const startY = widgetHeight + 30; 
                            const maxW = this.size[0] - 20;
                            const maxH = this.size[1] - startY - 10;
                            
                            if (maxH > 20) {
                                const ratio = Math.min(maxW / img.naturalWidth, maxH / img.naturalHeight);
                                const drawW = img.naturalWidth * ratio;
                                const drawH = img.naturalHeight * ratio;
                                const drawX = 10 + (maxW - drawW) / 2;
                                const drawY = startY + (maxH - drawH) / 2;
                                ctx.drawImage(img, drawX, drawY, drawW, drawH);
                            }
                        }
                    }
                };

                // 4. Custom node size calculation
                const computeSize = node.computeSize;
                node.computeSize = function (out) {
                    let size = computeSize ? computeSize.apply(this, arguments) : [200, 200];
                    
                    const previewToggle = this.widgets?.find(w => w.name === "preview_image");
                    if (previewToggle && previewToggle.value && this.imgs && this.imgs.length > 0) {
                        const img = this.imgs[0];
                        if (img && img.complete && img.naturalWidth > 0) {
                            const ratio = size[0] / img.naturalWidth;
                            size[1] += img.naturalHeight * ratio;
                        } else {
                            size[1] += 200; // placeholder height while loading
                        }
                    }
                    return size;
                };

                // 5. Instantly clear image/resize when toggle clicked
                const previewWidget = node.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        
                        if (val) {
                            // Turned ON: Try to fetch the image preview manually
                            const fileWidget = node.widgets.find(w => w.name === "image_file");
                            if (fileWidget && fileWidget.value) {
                                node.imgs = [new Image()];
                                node.imgs[0].onload = () => {
                                    app.graph.setDirtyCanvas(true, true);
                                    if (node.setSize && node.computeSize) node.setSize(node.computeSize());
                                };
                                node.imgs[0].src = api.apiURL(`/view?filename=${encodeURIComponent(fileWidget.value)}&type=input`);
                            }
                        } else {
                            // Turned OFF: Clear and shrink
                            node.imgs = null;
                            if (node.imageIndex !== undefined) node.imageIndex = 0;
                            app.graph.setDirtyCanvas(true, true);
                            if (node.setSize && node.computeSize) node.setSize(node.computeSize());
                        }
                    };
                }
            };
            
            // 6. Fetch preview when workflow is loaded
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                if (onConfigure) onConfigure.apply(this, arguments);
                
                const previewToggle = this.widgets?.find(w => w.name === "preview_image");
                const fileWidget = this.widgets?.find(w => w.name === "image_file");
                
                if (previewToggle && previewToggle.value && fileWidget && fileWidget.value) {
                    this.imgs = [new Image()];
                    this.imgs[0].onload = () => {
                        app.graph.setDirtyCanvas(true, true);
                        if (this.setSize && this.computeSize) this.setSize(this.computeSize());
                    };
                    this.imgs[0].src = api.apiURL(`/view?filename=${encodeURIComponent(fileWidget.value)}&type=input`);
                }
            };
        }

        // ====================================================================
        // Honda_SaveImage: Only prevent ComfyUI drawing overrides
        // ====================================================================
        if (nodeData.name === "Honda_SaveImage") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                
                const node = this;

                let _realImgs = node.imgs;
                Object.defineProperty(node, "imgs", {
                    get: function() {
                        const previewWidget = this.widgets?.find(w => w.name === "preview_image");
                        if (previewWidget && !previewWidget.value) return null;
                        return _realImgs;
                    },
                    set: function(val) { _realImgs = val; },
                    configurable: true
                });

                let _realOnDrawBackground = node.onDrawBackground;
                Object.defineProperty(node, "onDrawBackground", {
                    get: function() {
                        return function(ctx) {
                            const previewWidget = this.widgets?.find(w => w.name === "preview_image");
                            if (previewWidget && !previewWidget.value) return;
                            if (_realOnDrawBackground) _realOnDrawBackground.apply(this, arguments);
                            else if (nodeType.prototype.onDrawBackground) nodeType.prototype.onDrawBackground.apply(this, arguments);
                        };
                    },
                    set: function(val) { _realOnDrawBackground = val; },
                    configurable: true
                });

                const previewWidget = node.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        app.graph.setDirtyCanvas(true, true);
                        if (node.setSize && node.computeSize) node.setSize(node.computeSize());
                    };
                }
            };
        }
    }
});

// Helper for file upload
async function uploadFile(node, file) {
    const body = new FormData();
    body.append("image", file);
    body.append("type", "input");
    
    try {
        const resp = await api.fetchApi("/upload/image", { method: "POST", body });
        const data = await resp.json();
        
        if (data.name) {
            // Update the string widget
            const fileWidget = node.widgets.find(w => w.name === "image_file");
            if (fileWidget) fileWidget.value = data.name;
            
            // Set up preview
            const previewToggle = node.widgets.find(w => w.name === "preview_image");
            if (previewToggle && previewToggle.value) {
                node.imgs = [new Image()];
                node.imgs[0].onload = () => {
                    app.graph.setDirtyCanvas(true, true);
                    if (node.setSize && node.computeSize) node.setSize(node.computeSize());
                };
                node.imgs[0].src = api.apiURL(`/view?filename=${encodeURIComponent(data.name)}&type=input&subfolder=${data.subfolder || ""}`);
            }
        }
    } catch (e) {
        console.error("[Honda Nodes] Image upload failed", e);
    }
}
