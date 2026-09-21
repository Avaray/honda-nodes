import { app } from "../../../scripts/app.js";

const NODE_TYPE = "Honda_ExtractMetadata";
const STYLE_ID = "honda-extract-metadata-style";

// After each run, also write the resolved path into the "file_path" widget,
// so the field shows the path even when it is fed by a link.
// Set to false if you only want the path shown inside the preview panel.
const SYNC_PATH_WIDGET = true;

const EMPTY_PATH = "Path appears after the node runs.";
const EMPTY_TEXT = "Metadata appears here after the node runs.";
const NO_METADATA = "mex returned no metadata for this file.";

const CSS = `
.hem {
    display: flex;
    flex-direction: column;
    gap: 4px;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.hem-head {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--descrip-text, #999);
}
.hem-path {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.hem-copy {
    flex: none;
    padding: 1px 8px;
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
    background: transparent;
    color: var(--input-text, #ddd);
    font: inherit;
    cursor: pointer;
}
.hem-copy:hover { background: var(--comfy-input-bg, #222); }
.hem-text {
    flex: 1;
    min-height: 60px;
    box-sizing: border-box;
    padding: 6px;
    resize: none;
    overflow: auto;
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
    background: var(--comfy-input-bg, #222);
    color: var(--input-text, #ddd);
    font: inherit;
}
`;

function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = CSS;
    document.head.appendChild(style);
}

// ui values arrive as arrays (Python tuples); tolerate plain values too.
const first = (v) => (Array.isArray(v) ? v[0] : v);

// mex -j output: pretty-print it. Plain-text output is shown untouched.
function prettify(text) {
    const t = (text ?? "").trim();
    if (t.startsWith("{") || t.startsWith("[")) {
        try {
            return JSON.stringify(JSON.parse(t), null, 2);
        } catch {
            /* not valid JSON - fall through and show as is */
        }
    }
    return text ?? "";
}

function buildPanel() {
    const root = document.createElement("div");
    root.className = "hem";

    const head = document.createElement("div");
    head.className = "hem-head";

    const path = document.createElement("span");
    path.className = "hem-path";
    path.textContent = EMPTY_PATH;

    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "hem-copy";
    copyBtn.textContent = "Copy metadata";

    head.append(path, copyBtn);

    const area = document.createElement("textarea");
    area.className = "hem-text";
    area.readOnly = true;
    area.spellcheck = false;
    area.wrap = "off";
    area.placeholder = EMPTY_TEXT;

    copyBtn.onclick = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        let label = "Copied";
        try {
            await navigator.clipboard.writeText(area.value);
        } catch {
            label = "Copy failed";
        }
        copyBtn.textContent = label;
        setTimeout(() => (copyBtn.textContent = "Copy metadata"), 1000);
    };

    root.append(head, area);
    return { root, path, area };
}

app.registerExtension({
    name: "HondaNodes.ExtractMetadata",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_TYPE) return;

        injectStyles();

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            const panel = buildPanel();
            this._hemPanel = panel;

            const widget = this.addDOMWidget("metadata_preview", "div", panel.root, {
                serialize: false,
                getMinHeight: () => 140,
            });
            // Keep the preview out of the saved workflow (metadata can be large).
            widget.serialize = false;
        };

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            const panel = this._hemPanel;
            if (!panel) return;

            const resolvedPath = first(message?.resolved_path);
            const metadataText = first(message?.metadata_text);

            if (resolvedPath !== undefined) {
                panel.path.textContent = resolvedPath;
                panel.path.title = resolvedPath;

                if (SYNC_PATH_WIDGET) {
                    const pathWidget = this.widgets?.find((w) => w.name === "file_path");
                    if (pathWidget) pathWidget.value = resolvedPath;
                }
            }

            if (metadataText !== undefined) {
                panel.area.value = prettify(metadataText);
                panel.area.placeholder = metadataText ? "" : NO_METADATA;
            }

            this.setDirtyCanvas?.(true, true);
        };
    },
});
