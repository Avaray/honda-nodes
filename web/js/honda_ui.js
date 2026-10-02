import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "HondaNodes.UI",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (["Honda_LoadImage", "Honda_SaveImage"].includes(nodeData.name)) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                
                const node = this;

                // 1. Indestructible hook for `imgs` property
                // This prevents ComfyUI from expanding the node or rendering cached images
                // whenever the preview toggle is OFF.
                let _realImgs = node.imgs;
                Object.defineProperty(node, "imgs", {
                    get: function() {
                        const previewWidget = this.widgets?.find(w => w.name === "preview_image");
                        if (previewWidget && !previewWidget.value) {
                            return null;
                        }
                        return _realImgs;
                    },
                    set: function(val) {
                        _realImgs = val;
                    },
                    configurable: true
                });

                // 2. Indestructible hook for `onDrawBackground`
                // Prevents ComfyUI core extensions from overwriting our render blocking.
                let _realOnDrawBackground = node.onDrawBackground;
                Object.defineProperty(node, "onDrawBackground", {
                    get: function() {
                        return function(ctx) {
                            const previewWidget = this.widgets?.find(w => w.name === "preview_image");
                            if (previewWidget && !previewWidget.value) {
                                return; // Block drawing completely
                            }
                            if (_realOnDrawBackground) {
                                _realOnDrawBackground.apply(this, arguments);
                            } else if (nodeType.prototype.onDrawBackground) {
                                nodeType.prototype.onDrawBackground.apply(this, arguments);
                            }
                        };
                    },
                    set: function(val) {
                        _realOnDrawBackground = val;
                    },
                    configurable: true
                });

                // 3. Trigger immediate updates when toggle is clicked
                const previewWidget = node.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        
                        if (val) {
                            // If turned ON, trigger the image widget to reload so it shows immediately
                            const imageWidget = node.widgets?.find(w => w.name === "image");
                            if (imageWidget && imageWidget.callback) {
                                imageWidget.callback(imageWidget.value);
                            }
                        }
                        
                        // Force a redraw and resize of the node
                        app.graph.setDirtyCanvas(true, true);
                        if (node.setSize && node.computeSize) {
                            node.setSize(node.computeSize());
                        }
                    };
                }
            };
        }
    }
});
