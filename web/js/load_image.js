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
                    imageWidget.label = "[ OVERRIDDEN BY PATH ]";
                } else {
                    imageWidget.disabled = false;
                    imageWidget.label = "Image";
                }
            }

            // Disable max_resolution when lightweight_preview is off
            const lwWidget = node.widgets?.find(w => w.name === "lightweight_preview");
            const maxResWidget = node.widgets?.find(w => w.name === "max_resolution");
            if (lwWidget && maxResWidget) {
                maxResWidget.disabled = !lwWidget.value;
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

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            if (onNodeCreated) {
                onNodeCreated.apply(this, arguments);
            }
            const node = this;
            // Watch the lightweight_preview toggle
            const lwWidget = node.widgets?.find(w => w.name === "lightweight_preview");
            if (lwWidget) {
                const origCallback = lwWidget.callback;
                lwWidget.callback = function(value) {
                    if (origCallback) origCallback.apply(this, arguments);
                    updateWidgetState(node);
                    node.setDirtyCanvas(true, true);
                };
            }
            updateWidgetState(node);
        };
    }
});
