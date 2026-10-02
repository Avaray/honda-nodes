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

                // 1. Hide the standard image_file string widget
                const fileWidget = node.widgets?.find(w => w.name === "image_file");
                if (fileWidget) {
                    fileWidget.hidden = true;
                    fileWidget.computeSize = () => [0, -4]; // take zero space
                }

                // 2. Helper to compute layout positions dynamically
                node.getLayout = function() {
                    let y = 30; // base offset for node header
                    if (this.widgets) {
                        for (let w of this.widgets) {
                            if (!w.hidden && w.computeSize) {
                                y += w.computeSize()[1] + 4;
                            }
                        }
                    }
                    y += 10; // extra padding

                    const layout = {};
                    
                    // Drag & drop zone (taller)
                    layout.dnd = { x: 10, y: y, w: Math.max(this.size[0] - 20, 10), h: 60 };
                    y += layout.dnd.h + 10;
                    
                    // File name text (wrapped)
                    const fileName = fileWidget ? fileWidget.value : "";
                    let lines = [];
                    if (fileName) {
                        // approx characters that fit per line (assuming 12px font)
                        const charsPerLine = Math.floor((this.size[0] - 20) / 6.5);
                        let str = fileName;
                        while(str.length > 0) {
                            lines.push(str.substring(0, Math.max(charsPerLine, 10)));
                            str = str.substring(charsPerLine);
                        }
                    }
                    layout.fileName = { lines, x: 10, y: y, h: lines.length * 15 };
                    if (lines.length > 0) y += layout.fileName.h + 10;
                    
                    // Preview image
                    const previewToggle = this.widgets?.find(w => w.name === "preview_image");
                    layout.preview = null;
                    if (previewToggle && previewToggle.value && this.imgs && this.imgs.length > 0) {
                        const img = this.imgs[0];
                        if (img && img.complete && img.naturalWidth > 0) {
                            const maxW = this.size[0] - 20;
                            const ratio = maxW / img.naturalWidth;
                            const drawH = img.naturalHeight * ratio;
                            layout.preview = { img, x: 10, y: y, w: maxW, h: drawH };
                            y += drawH + 10;
                        } else {
                            layout.preview = { placeholder: true, x: 10, y: y, w: this.size[0] - 20, h: 100 };
                            y += 110;
                        }
                    }
                    
                    layout.totalHeight = y;
                    return layout;
                };

                // 3. Custom Node Size Calculation
                node.computeSize = function (out) {
                    const minSize = [250, 100];
                    const layout = this.getLayout();
                    return [Math.max(this.size[0], minSize[0]), layout.totalHeight];
                };

                // 4. Handle clicks on Drag & Drop zone
                node.onMouseDown = function(e, local_pos) {
                    const layout = this.getLayout();
                    if (local_pos[0] >= layout.dnd.x && local_pos[0] <= layout.dnd.x + layout.dnd.w &&
                        local_pos[1] >= layout.dnd.y && local_pos[1] <= layout.dnd.y + layout.dnd.h) {
                        
                        // Open file picker
                        const fileInput = document.createElement("input");
                        fileInput.type = "file";
                        fileInput.accept = "image/*";
                        fileInput.onchange = (ev) => {
                            const file = ev.target.files[0];
                            if (file) uploadFile(this, file);
                        };
                        fileInput.click();
                        return true;
                    }
                    return false;
                };

                // 5. Add Drag & Drop handlers
                node.onDragOver = function(e) { return true; };
                node.onDragDrop = function(e) {
                    if (e.dataTransfer && e.dataTransfer.files) {
                        const file = e.dataTransfer.files[0];
                        if (file && file.type.startsWith("image/")) {
                            uploadFile(node, file);
                            return true;
                        }
                    }
                    return false;
                };
                node.onDropFile = function(file) {
                    if (file && file.type.startsWith("image/")) {
                        uploadFile(node, file);
                        return true;
                    }
                    return false;
                };

                // 6. Custom Full Node Render
                const instDraw = node.onDrawBackground;
                node.onDrawBackground = function (ctx) {
                    if (instDraw) instDraw.apply(this, arguments);
                    else if (nodeType.prototype.onDrawBackground) nodeType.prototype.onDrawBackground.apply(this, arguments);

                    const layout = this.getLayout();

                    // Draw D&D Box
                    ctx.save();
                    ctx.strokeStyle = "#666";
                    ctx.setLineDash([6, 6]);
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.roundRect(layout.dnd.x, layout.dnd.y, layout.dnd.w, layout.dnd.h, 6);
                    ctx.stroke();
                    
                    ctx.fillStyle = "#aaa";
                    ctx.font = "14px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText("📂 Click or Drop Image", layout.dnd.x + layout.dnd.w/2, layout.dnd.y + layout.dnd.h/2 + 5);
                    ctx.restore();

                    // Draw File name
                    if (layout.fileName.lines.length > 0) {
                        ctx.save();
                        ctx.fillStyle = "#888";
                        ctx.font = "12px Arial";
                        ctx.textAlign = "left";
                        let ty = layout.fileName.y + 12;
                        for (let line of layout.fileName.lines) {
                            ctx.fillText(line, layout.fileName.x, ty);
                            ty += 15;
                        }
                        ctx.restore();
                    }

                    // Draw Preview
                    if (layout.preview) {
                        if (layout.preview.img) {
                            ctx.drawImage(layout.preview.img, layout.preview.x, layout.preview.y, layout.preview.w, layout.preview.h);
                        } else {
                            ctx.fillStyle = "#333";
                            ctx.fillRect(layout.preview.x, layout.preview.y, layout.preview.w, layout.preview.h);
                            ctx.fillStyle = "#888";
                            ctx.textAlign = "center";
                            ctx.font = "14px Arial";
                            ctx.fillText("Loading...", layout.preview.x + layout.preview.w/2, layout.preview.y + layout.preview.h/2 + 5);
                        }
                    }
                };

                // 7. Instantly clear image/resize when toggle clicked
                const previewWidget = node.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        
                        if (val) {
                            if (fileWidget && fileWidget.value) {
                                node.imgs = [new Image()];
                                node.imgs[0].onload = () => {
                                    app.graph.setDirtyCanvas(true, true);
                                    if (node.setSize) node.setSize(node.computeSize());
                                };
                                node.imgs[0].src = api.apiURL(`/view?filename=${encodeURIComponent(fileWidget.value)}&type=input&t=${Date.now()}`);
                            }
                        } else {
                            node.imgs = null;
                            if (node.imageIndex !== undefined) node.imageIndex = 0;
                            app.graph.setDirtyCanvas(true, true);
                            if (node.setSize) node.setSize(node.computeSize());
                        }
                    };
                }
            };
            
            // 8. Fetch preview when workflow is loaded
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                if (onConfigure) onConfigure.apply(this, arguments);
                
                const previewToggle = this.widgets?.find(w => w.name === "preview_image");
                const fileWidget = this.widgets?.find(w => w.name === "image_file");
                
                if (previewToggle && previewToggle.value && fileWidget && fileWidget.value) {
                    this.imgs = [new Image()];
                    this.imgs[0].onload = () => {
                        app.graph.setDirtyCanvas(true, true);
                        if (this.setSize) this.setSize(this.computeSize());
                    };
                    this.imgs[0].src = api.apiURL(`/view?filename=${encodeURIComponent(fileWidget.value)}&type=input&t=${Date.now()}`);
                }
            };
        }

        // ====================================================================
        // Honda_SaveImage: Keep overrides to block drawing
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
                    if (node.setSize) node.setSize(node.computeSize());
                };
                node.imgs[0].src = api.apiURL(`/view?filename=${encodeURIComponent(data.name)}&type=input&t=${Date.now()}`);
            } else {
                app.graph.setDirtyCanvas(true, true);
                if (node.setSize) node.setSize(node.computeSize());
            }
        }
    } catch (e) {
        console.error("[Honda Nodes] Image upload failed", e);
    }
}
