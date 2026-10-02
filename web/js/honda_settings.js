import { app } from "../../../scripts/app.js";

const HONDA_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 512 512"><path fill="currentColor" d="M254.1 18.63c-81.4 0-231.43 155.97-171.63 300.77c8 25.3 27.83 50.4 49.13 77.1c24.4 30.6 51.6 63.2 68.7 96.9h20.5c-18.1-39.8-48.5-75.9-74.6-108.6c-27.4-34.3-48.73-65.2-48.73-87.9c.1-9.1 2.23-18.1 5.53-26.3c23-61.4 114-119.7 148.5-135l3.6-2l3.9 1.3c60.9 20.9 129.3 66.7 154 135.7c4.1 11.7 5.9 18 5.6 27.3c-.5 15.8-24.5 54.7-55 88.7c-29.1 32.4-62.4 67.7-80 106.7h20.5c16.8-32.2 46.2-64 73.3-94.2c23.2-25.6 45.3-50 54.9-74.8c52.9-124-99.2-305.67-178.2-305.67m.8 135.47c-38.7 21.5-85.1 52.2-113.7 88.2c9.7 83 59 146.1 118.3 146.1c59.2 0 108.3-62.7 118.2-145.3c-28.9-42.1-78-72.9-122.8-89m-58.3 83h2.4c13.1.1 26.1 2.7 39.1 7.4c-16.8 40.6-59 42-78.1 0c12.2-4.8 24.4-7.2 36.6-7.4m124.9 0c13-.1 26 2.3 39.1 7.4c-19.2 42-61.3 40.6-78.2 0c13.1-4.7 26.1-7.3 39.1-7.4"/></svg>`;

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

        // Register a placeholder setting to ensure the "HondaNodes" tab exists in the settings modal
        app.ui.settings.addSetting({
            id: "HondaNodes.Placeholder",
            name: "🖼️ Honda Nodes",
            type: "boolean",
            defaultValue: false,
            tooltip: "Placeholder setting. More features coming soon.",
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

                    const openAndClickTab = () => {
                        const allEls = Array.from(document.querySelectorAll(
                            '.p-menuitem-text, .p-tabview-title, span, a, button, li'
                        ));
                        // Find the "Other" tab on the left side
                        const otherTab = allEls.find(el => el.textContent && el.textContent.trim() === 'Other');
                        if (otherTab) {
                            const btn = otherTab.closest('a, button, li, [role="menuitem"], [role="tab"]');
                            if (btn) btn.click();
                            else otherTab.click();

                            // Give it a moment to render the right pane, then scroll to HondaNodes
                            setTimeout(() => {
                                const allText = Array.from(document.querySelectorAll('span, div, h2, h3'));
                                const hondaHeader = allText.find(el => el.textContent && el.textContent.trim() === 'HondaNodes');
                                if (hondaHeader) {
                                    hondaHeader.scrollIntoView({ behavior: "smooth", block: "start" });
                                }
                            }, 150);
                        }
                    };

                    const settingsBtn =
                        document.querySelector('button[aria-label="Settings"]') ||
                        document.querySelector('button[title="Settings"]') ||
                        document.querySelector('.comfy-settings-btn') ||
                        document.querySelector('.pi-cog')?.closest('button');

                    if (settingsBtn) {
                        settingsBtn.click();
                        setTimeout(openAndClickTab, 300);
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
        // Clear images on the frontend instantly when the toggle is turned off
        if (["Honda_LoadImage", "Honda_SaveImage"].includes(nodeData.name)) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                
                const previewWidget = this.widgets?.find(w => w.name === "preview_image");
                if (previewWidget) {
                    const node = this;
                    const origCallback = previewWidget.callback;
                    previewWidget.callback = function(val) {
                        if (origCallback) origCallback.apply(this, arguments);
                        if (!val) {
                            node.imgs = null;
                            app.graph.setDirtyCanvas(true, true);
                        }
                    };
                }
            };
        }
    }
});
