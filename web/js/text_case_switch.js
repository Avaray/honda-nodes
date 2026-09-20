import { app } from "../../../scripts/app.js";

const NODE_TYPE = "Honda_TextCaseSwitch";

// Widget names to collapse to single-line height by default
const COMPACT_WIDGETS = ["cases", "default_output"];

// Approximate single-line height in LiteGraph canvas units
const SINGLE_LINE_HEIGHT = 22;

app.registerExtension({
    name: "HondaNodes.TextCaseSwitch",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_TYPE) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            for (const widget of this.widgets ?? []) {
                if (!COMPACT_WIDGETS.includes(widget.name)) continue;

                // Override computeSize to report a minimal height
                widget.computeSize = () => [0, SINGLE_LINE_HEIGHT];

                // Allow manual resizing via the widget's resize handle
                widget.options = widget.options ?? {};
                widget.options.getMinHeight = () => SINGLE_LINE_HEIGHT;
            }

            // Re-fit the node to its new, smaller widget layout
            this.setSize(this.computeSize());
            this.graph?.setDirtyCanvas(true, true);
        };
    },
});
