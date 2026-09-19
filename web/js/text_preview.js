// Honda Nodes - Text Preview widget extension
// Hooks into ComfyUI's textPreviewWidgets system to render text output
// on the Honda_TextPreview node body after execution.

import { app } from "../../scripts/app.js";

const NODE_TYPE = "Honda_TextPreview";

app.registerExtension({
    name: "HondaNodes.TextPreview",

    async nodeCreated(node) {
        if (node.comfyClass !== NODE_TYPE) return;

        // Attempt to use the native V3 textPreviewWidgets API if available.
        // This API adds a readonly textarea to the node that gets updated
        // reactively from the backend ui output {"text": (value,)}.
        try {
            const { addTextPreviewWidgets } = await import(
                "../../extensions/core/textPreviewWidgets.js"
            );
            addTextPreviewWidgets(node);
        } catch (e) {
            // Fallback: manually add a simple read-only textarea widget
            // using the legacy LiteGraph DOM widget API.
            const container = document.createElement("div");
            container.style.padding = "4px";
            container.style.width = "100%";

            const textarea = document.createElement("textarea");
            textarea.style.width = "100%";
            textarea.style.minHeight = "60px";
            textarea.style.resize = "vertical";
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

            // Store reference on the node for the afterQueued callback.
            node._hondaPreviewTextarea = textarea;

            node.addDOMWidget("text_preview_widget", "div", container, {
                getValue: () => textarea.value,
                setValue: (v) => { textarea.value = v ?? ""; },
            });
        }
    },

    async afterQueued() {
        // Called after the queue finishes. Walk all nodes and update the
        // fallback textarea if the native preview didn't activate.
        for (const node of app.graph.nodes ?? []) {
            if (node.comfyClass !== NODE_TYPE) continue;
            if (!node._hondaPreviewTextarea) continue;

            const output = app.nodeOutputs?.[node.id];
            if (output?.text) {
                const val = Array.isArray(output.text)
                    ? output.text[0]
                    : output.text;
                node._hondaPreviewTextarea.value = val ?? "";
                node.setDirtyCanvas(true);
            }
        }
    },
});
