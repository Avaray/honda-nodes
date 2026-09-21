import { app } from "../../../scripts/app.js";

const NODE_TYPE = "Honda_JSONPreview";

// Helper to construct jq-compatible paths
function makePath(parentPath, key, isArray) {
    if (parentPath === null) return ""; // root is empty, but we'll default to "." when copying
    if (isArray) {
        return `${parentPath}[${key}]`;
    } else {
        // if key has spaces or special chars, use bracket notation, else dot notation
        if (/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(key)) {
            return parentPath === "" ? `.${key}` : `${parentPath}.${key}`;
        } else {
            return `${parentPath}["${key.replace(/"/g, '\\"')}"]`;
        }
    }
}

// Build copy button DOM element
function buildCopyButton(path) {
    const copyBtn = document.createElement("span");
    copyBtn.innerHTML = " 📋";
    copyBtn.style.cursor = "pointer";
    copyBtn.style.opacity = "0";
    copyBtn.style.transition = "opacity 0.2s";
    
    const finalPath = path || ".";
    copyBtn.title = "Copy path: " + finalPath;
    
    copyBtn.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        navigator.clipboard.writeText(finalPath).catch(err => console.error("Copy failed", err));
        const old = copyBtn.innerHTML;
        copyBtn.innerHTML = " ✔️";
        setTimeout(() => copyBtn.innerHTML = old, 1000);
    };
    return copyBtn;
}

function buildJsonTree(obj, key = null, parentPath = null, isArrayChild = false, autoCollapseGetter) {
    const currentPath = makePath(parentPath, key, isArrayChild);

    if (obj === null) return createNode(key, "null", "gray", currentPath);
    if (typeof obj === "boolean") return createNode(key, obj, "#d33682", currentPath);
    if (typeof obj === "number") return createNode(key, obj, "#cb4b16", currentPath);
    if (typeof obj === "string") return createNode(key, `"${obj}"`, "#859900", currentPath);
    
    if (Array.isArray(obj)) {
        if (obj.length === 0) return createNode(key, "[]", "var(--input-text, #ddd)", currentPath);
        
        const details = document.createElement("details");
        details.open = key === null; 
        
        const summary = document.createElement("summary");
        summary.innerHTML = key !== null ? `<strong>${key}</strong>: Array(${obj.length})` : `Array(${obj.length})`;
        summary.style.cursor = "pointer";
        summary.style.userSelect = "none";
        summary.style.color = "var(--input-text, #ddd)";
        summary.style.position = "relative";
        
        const copyBtn = buildCopyButton(currentPath);
        summary.appendChild(copyBtn);
        summary.onmouseenter = () => copyBtn.style.opacity = "0.7";
        summary.onmouseleave = () => copyBtn.style.opacity = "0";

        details.appendChild(summary);
        
        const container = document.createElement("div");
        container.style.marginLeft = "12px";
        container.style.borderLeft = "1px solid var(--border-color, #555)";
        container.style.paddingLeft = "8px";
        
        obj.forEach((item, index) => {
            container.appendChild(buildJsonTree(item, index, currentPath, true, autoCollapseGetter));
        });
        
        details.appendChild(container);
        
        // Auto-collapse logic
        details.addEventListener("toggle", (e) => {
            if (details.open && autoCollapseGetter()) {
                const parent = details.parentElement;
                if (parent) {
                    for (const child of parent.children) {
                        if (child.tagName === "DETAILS" && child !== details) {
                            child.open = false;
                        }
                    }
                }
            }
        });

        return details;
    }
    
    // Object
    const keys = Object.keys(obj);
    if (keys.length === 0) return createNode(key, "{}", "var(--input-text, #ddd)", currentPath);
    
    const details = document.createElement("details");
    details.open = key === null;
    
    const summary = document.createElement("summary");
    summary.innerHTML = key !== null ? `<strong>${key}</strong>: Object` : `Object`;
    summary.style.cursor = "pointer";
    summary.style.userSelect = "none";
    summary.style.color = "var(--input-text, #ddd)";
    summary.style.position = "relative";

    const copyBtn = buildCopyButton(currentPath);
    summary.appendChild(copyBtn);
    summary.onmouseenter = () => copyBtn.style.opacity = "0.7";
    summary.onmouseleave = () => copyBtn.style.opacity = "0";

    details.appendChild(summary);
    
    const container = document.createElement("div");
    container.style.marginLeft = "12px";
    container.style.borderLeft = "1px solid var(--border-color, #555)";
    container.style.paddingLeft = "8px";
    
    keys.forEach(k => {
        container.appendChild(buildJsonTree(obj[k], k, currentPath, false, autoCollapseGetter));
    });
    
    details.appendChild(container);

    // Auto-collapse logic
    details.addEventListener("toggle", (e) => {
        if (details.open && autoCollapseGetter()) {
            const parent = details.parentElement;
            if (parent) {
                for (const child of parent.children) {
                    if (child.tagName === "DETAILS" && child !== details) {
                        child.open = false;
                    }
                }
            }
        }
    });

    return details;
}

function createNode(key, value, color, path) {
    const div = document.createElement("div");
    div.style.fontFamily = "monospace";
    div.style.fontSize = "12px";
    div.style.lineHeight = "1.5";
    div.style.whiteSpace = "pre-wrap";
    div.style.color = "var(--input-text, #ddd)";
    div.style.display = "flex";
    div.style.alignItems = "center";
    
    const safeValue = String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    const textSpan = document.createElement("span");
    if (key !== null) {
        textSpan.innerHTML = `<strong>${key}</strong>: <span style="color:${color}">${safeValue}</span>`;
    } else {
        textSpan.innerHTML = `<span style="color:${color}">${safeValue}</span>`;
    }
    
    const copyBtn = buildCopyButton(path);
    div.appendChild(textSpan);
    div.appendChild(copyBtn);

    div.onmouseenter = () => copyBtn.style.opacity = "0.7";
    div.onmouseleave = () => copyBtn.style.opacity = "0";

    return div;
}

app.registerExtension({
    name: "HondaNodes.JSONPreview",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_TYPE) return;

        // Create widget on node creation
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            const container = document.createElement("div");
            container.style.padding = "6px";
            container.style.width = "100%";
            container.style.height = "100%";
            container.style.minHeight = "120px";
            container.style.maxHeight = "400px";
            container.style.overflow = "hidden";
            container.style.display = "flex";
            container.style.flexDirection = "column";
            container.style.background = "var(--comfy-input-bg, #222)";
            container.style.border = "1px solid var(--border-color, #444)";
            container.style.borderRadius = "4px";
            container.style.boxSizing = "border-box";

            // Toolbar for auto-collapse toggle
            const toolbar = document.createElement("div");
            toolbar.style.display = "flex";
            toolbar.style.alignItems = "center";
            toolbar.style.marginBottom = "6px";
            toolbar.style.paddingBottom = "6px";
            toolbar.style.borderBottom = "1px solid var(--border-color, #444)";
            
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.id = "honda_json_autocollapse_" + this.id;
            checkbox.style.margin = "0 6px 0 0";
            
            const label = document.createElement("label");
            label.htmlFor = checkbox.id;
            label.innerText = "Auto-collapse siblings";
            label.style.color = "var(--input-text, #ccc)";
            label.style.fontSize = "12px";
            label.style.fontFamily = "sans-serif";
            label.style.cursor = "pointer";
            label.style.userSelect = "none";
            
            toolbar.appendChild(checkbox);
            toolbar.appendChild(label);
            container.appendChild(toolbar);

            const innerBox = document.createElement("div");
            innerBox.style.color = "var(--input-text, #999)";
            innerBox.style.fontFamily = "monospace";
            innerBox.style.fontSize = "12px";
            innerBox.style.overflow = "auto";
            innerBox.style.flex = "1";
            innerBox.innerHTML = "<i>(JSON tree will appear here after execution)</i>";
            
            container.appendChild(innerBox);
            
            this._hondaJsonPreviewContainer = innerBox;
            this._hondaJsonRawValue = "";
            this._hondaJsonAutoCollapseGetter = () => checkbox.checked;

            this.addDOMWidget("json_preview_widget", "div", container, {
                getValue: () => this._hondaJsonRawValue,
                setValue: (v) => { this._hondaJsonRawValue = v; },
            });
        };

        const renderJson = (node, val) => {
            node._hondaJsonRawValue = val;
            try {
                const parsed = JSON.parse(val);
                node._hondaJsonPreviewContainer.innerHTML = "";
                node._hondaJsonPreviewContainer.appendChild(
                    buildJsonTree(parsed, null, null, false, node._hondaJsonAutoCollapseGetter)
                );
            } catch (e) {
                node._hondaJsonPreviewContainer.innerHTML = `<span style="color:red">Invalid JSON: ${e.message}</span>`;
            }
            node.setDirtyCanvas(true, true);
        };

        // Update widget on node execution
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            if (this._hondaJsonPreviewContainer && message?.json_tree) {
                const val = Array.isArray(message.json_tree) ? message.json_tree[0] : message.json_tree;
                renderJson(this, val);
            }
        };

        // Update widget on outputs updated
        const onOutputsUpdated = nodeType.prototype.onNodeOutputsUpdated;
        nodeType.prototype.onNodeOutputsUpdated = function (outputs) {
            onOutputsUpdated?.apply(this, arguments);
            // In modern ComfyUI, onNodeOutputsUpdated handles node reload states
            const message = outputs?.[this.id];
            if (message?.json_tree && this._hondaJsonPreviewContainer) {
                const val = Array.isArray(message.json_tree) ? message.json_tree[0] : message.json_tree;
                renderJson(this, val);
            }
        }
    },

    onNodeOutputsUpdated(outputs) {
        // Fallback for older ComfyUI versions
        for (const [nodeId, message] of Object.entries(outputs)) {
            const node = app.graph.getNodeById(nodeId);
            if (node?.type === NODE_TYPE && node._hondaJsonPreviewContainer && message?.json_tree) {
                const val = Array.isArray(message.json_tree) ? message.json_tree[0] : message.json_tree;
                
                try {
                    const parsed = JSON.parse(val);
                    node._hondaJsonPreviewContainer.innerHTML = "";
                    node._hondaJsonPreviewContainer.appendChild(
                        buildJsonTree(parsed, null, null, false, node._hondaJsonAutoCollapseGetter)
                    );
                } catch (e) {
                    node._hondaJsonPreviewContainer.innerHTML = `<span style="color:red">Invalid JSON: ${e.message}</span>`;
                }
                node.setDirtyCanvas(true, true);
            }
        }
    }
});
