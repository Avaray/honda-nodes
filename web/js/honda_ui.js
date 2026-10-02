import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "HondaNodes.UI",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (["Honda_LoadImage", "Honda_SaveImage"].includes(nodeData.name)) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                
                const node = this;

                // 1. Intercept instance's onDrawBackground so it runs after ComfyUI core overrides
                const instDraw = node.onDrawBackground;
                node.onDrawBackground = function (ctx) {
                    const previewWidget = this.widgets?.find(w => w.name === "preview_image");
                    if (previewWidget && !previewWidget.value) {
                        return; // Skip drawing image completely
                    }
                    if (instDraw) {
                        instDraw.apply(this, arguments);
                    } else if (nodeType.prototype.onDrawBackground) {
                        nodeType.prototype.onDrawBackground.apply(this, arguments);
                    }
                };

                // 2. Clear cached frontend images immediately when the toggle is clicked off
                const previewWidget = node.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        if (!val) {
                            node.imgs = null;
                            if (node.imageIndex !== undefined) node.imageIndex = 0;
                        } else {
                            // Force ComfyUI to reload the combo image when turned ON
                            const imageWidget = node.widgets?.find(w => w.name === "image");
                            if (imageWidget && imageWidget.callback) {
                                imageWidget.callback(imageWidget.value);
                            }
                        }
                        app.graph.setDirtyCanvas(true, true);
                    };
                }
            };
        }
    }
});
