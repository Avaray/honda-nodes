import { app } from "../../../scripts/app.js";

const PREVIEW_NODES = ["Honda_TextPreview", "Honda_JSONGetValue"];



app.registerExtension({
    name: "HondaNodes.TextPreview",



    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (!PREVIEW_NODES.includes(nodeData.name)) return;

        // Create widget on node creation
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            const container = document.createElement("div");
            container.style.padding = "4px";
            container.style.width = "100%";
            // We give it a flexible height setup so it resizes well
            container.style.height = "100%";
            container.style.display = "flex";

            const textarea = document.createElement("textarea");
            textarea.style.width = "100%";
            textarea.style.flex = "1";
            textarea.style.minHeight = "60px";
            textarea.style.resize = "none"; // Disable manual resize to let ComfyUI layout handle it
            textarea.style.background = "var(--comfy-input-bg, #222)";
            textarea.style.color = "var(--input-text, #ddd)";
            textarea.style.border = "1px solid var(--border-color, #444)";
            textarea.style.borderRadius = "4px";
            textarea.style.fontFamily = "monospace";
            textarea.style.fontSize = "12px";
            textarea.style.padding = "6px";
            textarea.style.boxSizing = "border-box";
            textarea.readOnly = true;
            textarea.placeholder = "(output will appear here after execution)";

            container.appendChild(textarea);
            this._hondaPreviewTextarea = textarea;

            this.addDOMWidget("text_preview_widget", "div", container, {
                getValue: () => textarea.value,
                setValue: (v) => { textarea.value = v ?? ""; },
            });
        };

        // Update widget on node execution
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            if (this._hondaPreviewTextarea) {
                if (!message?.text) return;
                const val = Array.isArray(message.text) ? message.text[0] : message.text;
                this._hondaPreviewTextarea.value = val ?? "";
                this.setDirtyCanvas(true, true);
            }
        };
    },

    onNodeOutputsUpdated(outputs) {
        // Also update when outputs are bulk-updated (e.g. on workflow reload)
        for (const [nodeId, message] of Object.entries(outputs)) {
            const node = app.graph.getNodeById(nodeId);
            if (node && PREVIEW_NODES.includes(node.type)) {
                if (node._hondaPreviewTextarea) {
                    if (!message?.text) continue;
                    const val = Array.isArray(message.text) ? message.text[0] : message.text;
                    node._hondaPreviewTextarea.value = val ?? "";
                    node.setDirtyCanvas(true, true);
                }
            }
        }
    }
});
