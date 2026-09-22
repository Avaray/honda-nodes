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

// Build an icon button for copying text
function buildIconBtn(textToCopy, title, icon) {
    const btn = document.createElement("span");
    btn.innerHTML = " " + icon;
    btn.style.cursor = "pointer";
    btn.style.opacity = "0.3"; // Always visible
    btn.style.transition = "opacity 0.2s, transform 0.1s";
    btn.title = title;
    // Prevent it from shrinking or wrapping weirdly
    btn.style.display = "inline-block";
    btn.style.userSelect = "none";
    
    // Highlight when hovered
    btn.addEventListener("mouseenter", () => btn.style.opacity = "1");
    btn.addEventListener("mouseleave", () => btn.style.opacity = "0.6");
    
    btn.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        navigator.clipboard.writeText(textToCopy).catch(err => console.error("Copy failed", err));
        const old = btn.innerHTML;
        btn.innerHTML = " ✔️";
        setTimeout(() => btn.innerHTML = old, 1000);
    };
    return btn;
}

function buildJsonTree(obj, key = null, parentPath = null, isArrayChild = false, autoCollapseGetter, truncateGetter) {
    const currentPath = makePath(parentPath, key, isArrayChild);

    if (obj === null) return createNode(key, "null", "gray", currentPath, obj);
    if (typeof obj === "boolean") return createNode(key, obj, "#d33682", currentPath, obj);
    if (typeof obj === "number") return createNode(key, obj, "#cb4b16", currentPath, obj);
    if (typeof obj === "string") {
        let strToShow = obj;
        if (truncateGetter && truncateGetter() && strToShow.length > 80) {
            strToShow = strToShow.substring(0, 80) + "...";
        }
        return createNode(key, `"${strToShow}"`, "#859900", currentPath, obj);
    }
    
    if (Array.isArray(obj)) {
        if (obj.length === 0) return createNode(key, "[]", "var(--input-text, #ddd)", currentPath, obj);
        
        const details = document.createElement("details");
        details.open = key === null; 
        
        const summary = document.createElement("summary");
        summary.style.cursor = "pointer";
        summary.style.userSelect = "none";
        summary.style.color = "var(--input-text, #ddd)";
        summary.style.position = "relative";
        
        // Group key and buttons to prevent wrapping
        const headerSpan = document.createElement("span");
        headerSpan.style.whiteSpace = "nowrap";

        if (key !== null) {
            const keySpan = document.createElement("span");
            keySpan.innerHTML = `<strong>${key}</strong>`;
            headerSpan.appendChild(keySpan);
        }

        const copyPathBtn = buildIconBtn(currentPath || ".", "Copy path: " + (currentPath || "."), "📋");
        const copyValBtn = buildIconBtn(JSON.stringify(obj, null, 2), "Copy value (JSON)", "📄");
        
        headerSpan.appendChild(copyPathBtn);
        headerSpan.appendChild(copyValBtn);

        const typeSpan = document.createElement("span");
        typeSpan.innerHTML = key !== null ? `: Array(${obj.length})` : `Array(${obj.length})`;

        summary.appendChild(headerSpan);
        summary.appendChild(typeSpan);

        details.appendChild(summary);
        
        const container = document.createElement("div");
        container.style.marginLeft = "12px";
        container.style.borderLeft = "1px solid var(--border-color, #555)";
        container.style.paddingLeft = "8px";
        
        obj.forEach((item, index) => {
            container.appendChild(buildJsonTree(item, index, currentPath, true, autoCollapseGetter, truncateGetter));
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
    if (keys.length === 0) return createNode(key, "{}", "var(--input-text, #ddd)", currentPath, obj);
    
    const details = document.createElement("details");
    details.open = key === null;
    
    const summary = document.createElement("summary");
    summary.style.cursor = "pointer";
    summary.style.userSelect = "none";
    summary.style.color = "var(--input-text, #ddd)";
    summary.style.position = "relative";

    // Group key and buttons to prevent wrapping
    const headerSpan = document.createElement("span");
    headerSpan.style.whiteSpace = "nowrap";

    if (key !== null) {
        const keySpan = document.createElement("span");
        keySpan.innerHTML = `<strong>${key}</strong>`;
        headerSpan.appendChild(keySpan);
    }

    const copyPathBtn = buildIconBtn(currentPath || ".", "Copy path: " + (currentPath || "."), "📋");
    const copyValBtn = buildIconBtn(JSON.stringify(obj, null, 2), "Copy value (JSON)", "📄");
    
    headerSpan.appendChild(copyPathBtn);
    headerSpan.appendChild(copyValBtn);

    const typeSpan = document.createElement("span");
    typeSpan.innerHTML = key !== null ? `: Object` : `Object`;

    summary.appendChild(headerSpan);
    summary.appendChild(typeSpan);

    details.appendChild(summary);
    
    const container = document.createElement("div");
    container.style.marginLeft = "12px";
    container.style.borderLeft = "1px solid var(--border-color, #555)";
    container.style.paddingLeft = "8px";
    
    keys.forEach(k => {
        container.appendChild(buildJsonTree(obj[k], k, currentPath, false, autoCollapseGetter, truncateGetter));
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

function createNode(key, displayValue, color, path, rawValue) {
    const div = document.createElement("div");
    div.style.fontFamily = "monospace";
    div.style.fontSize = "12px";
    div.style.lineHeight = "1.5";
    div.style.whiteSpace = "pre-wrap";
    div.style.wordBreak = "break-all"; // Ensures super long strings wrap neatly
    div.style.color = "var(--input-text, #ddd)";
    // Use flex with flex-start so icons don't drift vertically on wrapped lines
    div.style.display = "flex";
    div.style.alignItems = "flex-start";
    
    const safeValue = String(displayValue).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    // The magic wrapper that prevents the key and buttons from wrapping
    const headerSpan = document.createElement("span");
    headerSpan.style.whiteSpace = "nowrap";
    
    if (key !== null) {
        const keySpan = document.createElement("span");
        keySpan.innerHTML = `<strong>${key}</strong>`;
        headerSpan.appendChild(keySpan);
    }
    
    const copyPathBtn = buildIconBtn(path || ".", "Copy path: " + (path || "."), "📋");
    const copyValBtn = buildIconBtn(
        typeof rawValue === "object" ? JSON.stringify(rawValue, null, 2) : String(rawValue), 
        "Copy value", 
        "📄"
    );
    headerSpan.appendChild(copyPathBtn);
    headerSpan.appendChild(copyValBtn);
    
    const sepSpan = document.createElement("span");
    sepSpan.innerText = key !== null ? ": " : "";
    sepSpan.style.whiteSpace = "pre";
    headerSpan.appendChild(sepSpan);
    
    const valSpan = document.createElement("span");
    valSpan.style.color = color;
    valSpan.innerHTML = safeValue;
    
    // Assemble the row
    div.appendChild(headerSpan);
    div.appendChild(valSpan);

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
            container.style.overflow = "hidden";
            container.style.display = "flex";
            container.style.flexDirection = "column";
            container.style.background = "var(--comfy-input-bg, #222)";
            container.style.border = "1px solid var(--border-color, #444)";
            container.style.borderRadius = "4px";
            container.style.boxSizing = "border-box";

            // Toolbar for auto-collapse toggle and truncate
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
            label.style.marginRight = "12px"; // Add space before next option
            
            const truncateCheckbox = document.createElement("input");
            truncateCheckbox.type = "checkbox";
            truncateCheckbox.id = "honda_json_truncate_" + this.id;
            truncateCheckbox.style.margin = "0 6px 0 0";
            // Checkbox event listener: re-render tree when toggled
            truncateCheckbox.addEventListener("change", () => {
                if (this._hondaJsonRawValue) {
                    renderJson(this, this._hondaJsonRawValue);
                }
            });

            const truncateLabel = document.createElement("label");
            truncateLabel.htmlFor = truncateCheckbox.id;
            truncateLabel.innerText = "Limit string length";
            truncateLabel.style.color = "var(--input-text, #ccc)";
            truncateLabel.style.fontSize = "12px";
            truncateLabel.style.fontFamily = "sans-serif";
            truncateLabel.style.cursor = "pointer";
            truncateLabel.style.userSelect = "none";

            toolbar.appendChild(checkbox);
            toolbar.appendChild(label);
            toolbar.appendChild(truncateCheckbox);
            toolbar.appendChild(truncateLabel);
            container.appendChild(toolbar);

            const relativeWrapper = document.createElement("div");
            relativeWrapper.style.flex = "1";
            relativeWrapper.style.position = "relative";

            const innerBox = document.createElement("div");
            innerBox.style.color = "var(--input-text, #999)";
            innerBox.style.fontFamily = "monospace";
            innerBox.style.fontSize = "12px";
            // Isolate scrollable content height from parent node
            innerBox.style.position = "absolute";
            innerBox.style.top = "0";
            innerBox.style.left = "0";
            innerBox.style.right = "0";
            innerBox.style.bottom = "0";
            innerBox.style.overflow = "auto";
            innerBox.innerHTML = "<i>(JSON tree will appear here after execution)</i>";
            
            relativeWrapper.appendChild(innerBox);
            container.appendChild(relativeWrapper);
            
            this._hondaJsonPreviewContainer = innerBox;
            this._hondaJsonRawValue = "";
            this._hondaJsonAutoCollapseGetter = () => checkbox.checked;
            this._hondaJsonTruncateGetter = () => truncateCheckbox.checked;

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
                    buildJsonTree(parsed, null, null, false, node._hondaJsonAutoCollapseGetter, node._hondaJsonTruncateGetter)
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
                        buildJsonTree(parsed, null, null, false, node._hondaJsonAutoCollapseGetter, node._hondaJsonTruncateGetter)
                    );
                } catch (e) {
                    node._hondaJsonPreviewContainer.innerHTML = `<span style="color:red">Invalid JSON: ${e.message}</span>`;
                }
                node.setDirtyCanvas(true, true);
            }
        }
    }
});
