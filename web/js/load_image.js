import { app } from "../../../scripts/app.js";

const NODE_TYPE = "Honda_LoadImage";

app.registerExtension({
    name: "HondaNodes.LoadImage",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_TYPE) return;
        
        const updateWidgetState = (node) => {
            const pathOverrideInput = node.inputs?.find(inp => inp.name === "path_override");
            const imageWidget = node.widgets?.find(w => w.name === "image");
            
            if (pathOverrideInput && imageWidget) {
                const isConnected = pathOverrideInput.link !== null && pathOverrideInput.link !== undefined;
                if (isConnected) {
                    imageWidget.disabled = true;
                    imageWidget.originalName = imageWidget.originalName || imageWidget.name;
                    imageWidget.name = "[ OVERRIDDEN BY PATH ]";
                } else {
                    imageWidget.disabled = false;
                    if (imageWidget.originalName) {
                        imageWidget.name = imageWidget.originalName;
                    }
                }
            }
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function(type, index, connected, link_info) {
            if (onConnectionsChange) {
                onConnectionsChange.apply(this, arguments);
            }
            if (type === 1) { // 1 = INPUT
                updateWidgetState(this);
                this.setDirtyCanvas(true, true);
            }
        };
        
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function() {
            if (onConfigure) {
                onConfigure.apply(this, arguments);
            }
            updateWidgetState(this);
        };
    }
});
