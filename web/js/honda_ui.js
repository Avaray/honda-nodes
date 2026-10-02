import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "HondaNodes.UI",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (["Honda_LoadImage", "Honda_SaveImage"].includes(nodeData.name)) {
            // 1. Intercept onDrawBackground to prevent ComfyUI from rendering images
            //    when the preview_image toggle is False.
            const onDrawBackground = nodeType.prototype.onDrawBackground;
            nodeType.prototype.onDrawBackground = function (ctx) {
                const previewWidget = this.widgets?.find(w => w.name === "preview_image");
                if (previewWidget && !previewWidget.value) {
                    // Skip calling the original onDrawBackground so neither the
                    // built-in image combo preview nor the execution preview are drawn.
                    return;
                }
                if (onDrawBackground) {
                    onDrawBackground.apply(this, arguments);
                }
            };

            // 2. Clear cached frontend images immediately when the toggle is clicked off
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                
                const previewWidget = this.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const node = this;
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        if (!val) {
                            node.imgs = null;
                        }
                        app.graph.setDirtyCanvas(true, true);
                    };
                }
            };
        }
    }
});
