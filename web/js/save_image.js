import { app } from "../../../scripts/app.js";

const NODE_TYPE = "Honda_SaveImage";

app.registerExtension({
    name: "HondaNodes.SaveImage",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_TYPE) return;

        const updateWidgetState = (node) => {
            const losslessWidget = node.widgets?.find(w => w.name === "webp_lossless");
            const qualityWidget = node.widgets?.find(w => w.name === "webp_quality");
            if (losslessWidget && qualityWidget) {
                qualityWidget.disabled = losslessWidget.value === true;
            }
        };

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);
            const node = this;

            // Watch the lossless toggle
            const losslessWidget = node.widgets?.find(w => w.name === "webp_lossless");
            if (losslessWidget) {
                const origCallback = losslessWidget.callback;
                losslessWidget.callback = function (value) {
                    if (origCallback) origCallback.apply(this, arguments);
                    updateWidgetState(node);
                    node.setDirtyCanvas(true, true);
                };
            }
            updateWidgetState(node);
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            if (onConfigure) onConfigure.apply(this, arguments);
            updateWidgetState(this);
        };
    }
});
