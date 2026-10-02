import { app } from "../../../scripts/app.js";

const HONDA_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 512 512"><path fill="currentColor" d="M254.1 18.63c-81.4 0-231.43 155.97-171.63 300.77c8 25.3 27.83 50.4 49.13 77.1c24.4 30.6 51.6 63.2 68.7 96.9h20.5c-18.1-39.8-48.5-75.9-74.6-108.6c-27.4-34.3-48.73-65.2-48.73-87.9c.1-9.1 2.23-18.1 5.53-26.3c23-61.4 114-119.7 148.5-135l3.6-2l3.9 1.3c60.9 20.9 129.3 66.7 154 135.7c4.1 11.7 5.9 18 5.6 27.3c-.5 15.8-24.5 54.7-55 88.7c-29.1 32.4-62.4 67.7-80 106.7h20.5c16.8-32.2 46.2-64 73.3-94.2c23.2-25.6 45.3-50 54.9-74.8c52.9-124-99.2-305.67-178.2-305.67m.8 135.47c-38.7 21.5-85.1 52.2-113.7 88.2c9.7 83 59 146.1 118.3 146.1c59.2 0 108.3-62.7 118.2-145.3c-28.9-42.1-78-72.9-122.8-89m-58.3 83h2.4c13.1.1 26.1 2.7 39.1 7.4c-16.8 40.6-59 42-78.1 0c12.2-4.8 24.4-7.2 36.6-7.4m124.9 0c13-.1 26 2.3 39.1 7.4c-19.2 42-61.3 40.6-78.2 0c13.1-4.7 26.1-7.3 39.1-7.4"/></svg>`;

const SETTING_MAX_RES = "HondaNodes.MaxResolutionDefault";

// Nodes that emit images and should show resolution info + respect global max_res
const HONDA_IMAGE_NODES = ["Honda_LoadImage", "Honda_SaveImage", "Honda_PreviewImage"];

// ---------------------------------------------------------------------------
// CSS injection
// ---------------------------------------------------------------------------
const HONDA_STYLE = `
.honda-menu-btn {
    background: transparent;
    border: none;
    color: var(--fg-color, #fff);
    cursor: pointer;
    padding: 4px 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background 0.2s;
}
.honda-menu-btn:hover {
    background: var(--bg-color-hover, rgba(255,255,255,0.1));
}
.honda-menu-popup {
    display: none;
    position: fixed;
    background: var(--bg-color, #2b2b2b);
    border: 1px solid var(--border-color, #444);
    border-radius: 6px;
    padding: 4px;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    min-width: 220px;
}
.honda-menu-item {
    padding: 8px 12px;
    cursor: pointer;
    color: var(--fg-color, #fff);
    border-radius: 4px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: background 0.2s;
}
.honda-menu-item:hover {
    background: var(--bg-color-hover, #444);
}
.honda-dims-label {
    font-size: 11px;
    text-align: center;
    padding: 2px 4px 4px;
    user-select: none;
    pointer-events: none;
}
.honda-dims-original {
    opacity: 0.45;
}
`;

// ---------------------------------------------------------------------------
// Extension
// ---------------------------------------------------------------------------
app.registerExtension({
    name: "HondaNodes.Settings",

    init() {
        // Inject styles
        const style = document.createElement("style");
        style.innerHTML = HONDA_STYLE;
        document.head.appendChild(style);

        // Register setting
        app.ui.settings.addSetting({
            id: SETTING_MAX_RES,
            name: "🖼️ Honda Nodes: Default Max Resolution",
            type: "slider",
            attrs: { min: 256, max: 8192, step: 256 },
            defaultValue: 1024,
            tooltip: "Maximum preview dimension (px) for Load Image, Save Image, and Preview Image nodes. Applies globally via serialization hook.",
        });
    },

    setup() {
        // -----------------------------------------------------------------------
        // Inject Honda Nodes top-bar button
        // -----------------------------------------------------------------------
        const injectButton = () => {
            const createButton = () => {
                const btn = document.createElement("button");
                btn.classList.add("comfyui-button", "honda-menu-btn");
                btn.innerHTML = HONDA_ICON;
                btn.title = "Honda Nodes";

                const popup = document.createElement("div");
                popup.classList.add("honda-menu-popup");

                // --- Settings item ---
                const btnSettings = document.createElement("div");
                btnSettings.classList.add("honda-menu-item");
                btnSettings.innerHTML = "⚙️ Settings (Honda Nodes)";
                btnSettings.onclick = () => {
                    popup.style.display = "none";

                    // Open settings and then navigate to the Honda section by clicking its tab.
                    const openAndClickTab = () => {
                        const allTabs = Array.from(document.querySelectorAll(
                            '.p-menuitem-link, .p-tabview-nav-link, button, [role="tab"], .settings-nav-item, li'
                        ));
                        // Look for a tab whose text content includes 'Honda'
                        const hondaTab = allTabs.find(el => el.textContent && el.textContent.toLowerCase().includes('honda'));
                        if (hondaTab) {
                            hondaTab.click();
                        } else {
                            // Fallback to search if tab not found
                            const searchInput = document.querySelector(
                                ".p-dialog .p-inputtext, [data-testid='settings-search'], .comfy-settings input[type='text'], .comfy-settings input[type='search']"
                            );
                            if (searchInput) {
                                searchInput.value = "Honda Nodes";
                                searchInput.dispatchEvent(new Event("input", { bubbles: true }));
                                searchInput.focus();
                            }
                        }
                    };

                    // Click the native settings button
                    const settingsBtn =
                        document.querySelector('button[aria-label="Settings"]') ||
                        document.querySelector('button[title="Settings"]') ||
                        document.querySelector('.comfy-settings-btn') ||
                        document.querySelector('.pi-cog')?.closest('button');

                    if (settingsBtn) {
                        settingsBtn.click();
                        // Give the dialog a bit more time to render side menu
                        setTimeout(openAndClickTab, 400);
                    } else {
                        console.warn("[Honda Nodes] Could not find native settings button.");
                    }
                };

                // --- GitHub item ---
                const btnGithub = document.createElement("div");
                btnGithub.classList.add("honda-menu-item");
                btnGithub.innerHTML = "⭐ Star on GitHub";
                btnGithub.onclick = () => {
                    window.open("https://github.com/Avaray/honda-nodes", "_blank");
                    popup.style.display = "none";
                };

                popup.appendChild(btnSettings);
                popup.appendChild(btnGithub);

                // Toggle popup
                btn.onclick = (e) => {
                    e.stopPropagation();
                    const isVisible = popup.style.display === "block";
                    popup.style.display = isVisible ? "none" : "block";
                    if (!isVisible) {
                        const rect = btn.getBoundingClientRect();
                        popup.style.top = (rect.bottom + 5) + "px";
                        popup.style.left = rect.left + "px";
                    }
                };

                // Close on outside click
                document.addEventListener("click", (e) => {
                    if (!btn.contains(e.target) && !popup.contains(e.target)) {
                        popup.style.display = "none";
                    }
                });

                document.body.appendChild(popup);
                return btn;
            };

            // Insert BEFORE the rgthree group if present, otherwise before settingsGroup
            const rgthreeGroup = document.querySelector(".rgthree-comfybar-top-button-group");
            if (rgthreeGroup) {
                const btn = createButton();
                rgthreeGroup.before(btn);
            } else if (app.menu?.settingsGroup?.element) {
                const btn = createButton();
                app.menu.settingsGroup.element.before(btn);
            } else {
                const menuGroup = document.querySelector(".comfyui-menu") || document.querySelector(".comfy-menu");
                if (menuGroup) {
                    const btn = createButton();
                    menuGroup.appendChild(btn);
                }
            }
        };

        // Small delay to ensure Vue + rgthree have both mounted
        setTimeout(injectButton, 1200);
    },

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (!HONDA_IMAGE_NODES.includes(nodeData.name)) return;

        // -----------------------------------------------------------------
        // Hide max_resolution widget visually (kept in schema for backend)
        // -----------------------------------------------------------------
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);
            const maxResWidget = this.widgets?.find(w => w.name === "max_resolution");
            if (maxResWidget) {
                maxResWidget.type = "converted-widget";
                maxResWidget.computeSize = () => [0, -4];
            }
        };

        // -----------------------------------------------------------------
        // Force the widget value to the setting value right before execution
        // (onBeforeRun triggers when Queue Prompt is clicked)
        // -----------------------------------------------------------------
        if (!app.hondaNodesGraphHooked) {
            app.hondaNodesGraphHooked = true;
            const origOnBeforeRun = app.graph.onBeforeRun;
            app.graph.onBeforeRun = function () {
                if (origOnBeforeRun) origOnBeforeRun.apply(this, arguments);
                const maxRes = app.ui.settings.getSettingValue(SETTING_MAX_RES, 1024);
                
                for (const node of app.graph.computeExecutionOrder(false)) {
                    if (HONDA_IMAGE_NODES.includes(node.type)) {
                        const widget = node.widgets?.find(w => w.name === "max_resolution");
                        if (widget) widget.value = maxRes;
                    }
                }
            };
        }

        // -----------------------------------------------------------------
        // onExecuted: display resolution info below the preview image
        // -----------------------------------------------------------------
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            if (onExecuted) onExecuted.apply(this, arguments);

            const rawWidget = this.widgets?.find(w => w.name === "raw_image");
            const isRaw = rawWidget?.value === true;
            const dims = message?.honda_dims;  // "previewWxpreviewH|origWxorigH"

            // Remove any previous label widget we added
            const prev = this.widgets?.find(w => w.name === "__honda_dims__");
            if (prev) {
                const idx = this.widgets.indexOf(prev);
                if (idx > -1) this.widgets.splice(idx, 1);
            }

            if (!dims) return;

            const [previewPart, origPart] = dims.split("|");
            const [pw, ph] = (previewPart || "").split("x").map(Number);
            const [ow, oh] = (origPart || "").split("x").map(Number);

            if (!pw || !ph) return;

            // Build a display-only widget that just renders text
            const labelWidget = {
                name: "__honda_dims__",
                type: "label",
                draw(ctx, node, widgetWidth, widgetY) {
                    const lineHeight = 18;
                    ctx.save();
                    ctx.font = "11px monospace";
                    ctx.textAlign = "center";

                    if (isRaw || !ow || !oh || (pw === ow && ph === oh)) {
                        // RAW mode or no scaling — show single line in normal colour
                        ctx.fillStyle = LiteGraph.WIDGET_TEXT_COLOR || "#ddd";
                        ctx.fillText(`${pw} × ${ph}`, widgetWidth * 0.5, widgetY + lineHeight * 0.75);
                    } else {
                        // Normal mode — show preview size + dimmed original
                        ctx.fillStyle = LiteGraph.WIDGET_TEXT_COLOR || "#ddd";
                        ctx.fillText(`Preview  ${pw} × ${ph}`, widgetWidth * 0.5, widgetY + lineHeight * 0.65);
                        ctx.globalAlpha = 0.45;
                        ctx.fillText(`(Original  ${ow} × ${oh})`, widgetWidth * 0.5, widgetY + lineHeight * 1.65);
                        ctx.globalAlpha = 1.0;
                    }
                    ctx.restore();
                },
                computeSize(width) {
                    const isRawNow = rawWidget?.value === true;
                    const sameSize = (!ow || !oh || (pw === ow && ph === oh));
                    return [width, isRawNow || sameSize ? 24 : 42];
                },
                serializeValue: () => undefined,
            };

            // Insert the label widget right before the image widget (last position before preview)
            this.widgets = this.widgets || [];
            this.widgets.push(labelWidget);
            this.setDirtyCanvas(true, true);
        };
    }
});
