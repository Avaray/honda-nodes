import { app } from "../../../scripts/app.js";

const HONDA_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 512 512"><path fill="currentColor" d="M254.1 18.63c-81.4 0-231.43 155.97-171.63 300.77c8 25.3 27.83 50.4 49.13 77.1c24.4 30.6 51.6 63.2 68.7 96.9h20.5c-18.1-39.8-48.5-75.9-74.6-108.6c-27.4-34.3-48.73-65.2-48.73-87.9c.1-9.1 2.23-18.1 5.53-26.3c23-61.4 114-119.7 148.5-135l3.6-2l3.9 1.3c60.9 20.9 129.3 66.7 154 135.7c4.1 11.7 5.9 18 5.6 27.3c-.5 15.8-24.5 54.7-55 88.7c-29.1 32.4-62.4 67.7-80 106.7h20.5c16.8-32.2 46.2-64 73.3-94.2c23.2-25.6 45.3-50 54.9-74.8c52.9-124-99.2-305.67-178.2-305.67m.8 135.47c-38.7 21.5-85.1 52.2-113.7 88.2c9.7 83 59 146.1 118.3 146.1c59.2 0 108.3-62.7 118.2-145.3c-28.9-42.1-78-72.9-122.8-89m-58.3 83h2.4c13.1.1 26.1 2.7 39.1 7.4c-16.8 40.6-59 42-78.1 0c12.2-4.8 24.4-7.2 36.6-7.4m124.9 0c13-.1 26 2.3 39.1 7.4c-19.2 42-61.3 40.6-78.2 0c13.1-4.7 26.1-7.3 39.1-7.4"/></svg>`;

const SETTING_LIGHTWEIGHT = "HondaNodes.LightweightPreviewDefault";
const SETTING_MAX_RES = "HondaNodes.MaxResolutionDefault";

app.registerExtension({
    name: "HondaNodes.Settings",
    init() {
        // Register native ComfyUI Settings
        app.ui.settings.addSetting({
            id: SETTING_LIGHTWEIGHT,
            name: "🖼️ Honda Nodes: Default Lightweight Preview",
            type: "boolean",
            defaultValue: true,
            tooltip: "If enabled, newly created 'Load Image' nodes will have Lightweight Preview turned on by default.",
        });

        app.ui.settings.addSetting({
            id: SETTING_MAX_RES,
            name: "🖼️ Honda Nodes: Default Max Resolution",
            type: "slider",
            attrs: { min: 256, max: 4096, step: 64 },
            defaultValue: 1024,
            tooltip: "Default Max Resolution for newly created 'Load Image' nodes.",
        });
    },
    setup() {
        // Inject CSS
        const style = document.createElement("style");
        style.type = "text/css";
        style.innerHTML = `
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
            background: var(--bg-color-hover, rgba(255, 255, 255, 0.1));
        }
        .honda-menu-popup {
            display: none;
            position: absolute;
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
        document.head.appendChild(style);

        // Build our custom menu button for the top/side bar
        const injectButton = () => {
            const createButton = () => {
                const btn = document.createElement("button");
                btn.classList.add("comfyui-button", "honda-menu-btn");
                btn.innerHTML = HONDA_ICON;
                btn.title = "Honda Nodes";
                
                const popup = document.createElement("div");
                popup.classList.add("honda-menu-popup");
                
                const btnSettings = document.createElement("div");
                btnSettings.classList.add("honda-menu-item");
                btnSettings.innerHTML = "⚙️ Settings (Honda Nodes)";
                btnSettings.onclick = () => {
                    app.ui.settings.show();
                    popup.style.display = "none";
                };

                const btnGithub = document.createElement("div");
                btnGithub.classList.add("honda-menu-item");
                btnGithub.innerHTML = "⭐ Star on GitHub";
                btnGithub.onclick = () => {
                    window.open("https://github.com/Avaray/honda-nodes", "_blank");
                    popup.style.display = "none";
                };

                popup.appendChild(btnSettings);
                popup.appendChild(btnGithub);
                
                // Toggle popup on click
                btn.onclick = (e) => {
                    e.stopPropagation();
                    const isVisible = popup.style.display === "block";
                    popup.style.display = isVisible ? "none" : "block";
                    
                    if (!isVisible) {
                        const rect = btn.getBoundingClientRect();
                        // Position below the button
                        popup.style.top = (rect.bottom + 5) + "px";
                        popup.style.left = rect.left + "px";
                    }
                };

                // Close when clicking outside
                document.addEventListener("click", (e) => {
                    if (!btn.contains(e.target) && !popup.contains(e.target)) {
                        popup.style.display = "none";
                    }
                });

                document.body.appendChild(popup);
                return btn;
            };

            // Attempt to inject into ComfyUI V3 menu top bar
            if (app.menu && app.menu.settingsGroup && app.menu.settingsGroup.element) {
                const btn = createButton();
                app.menu.settingsGroup.element.before(btn);
            } 
            // Fallback for older UI (V2) or other variants
            else {
                const menuGroup = document.querySelector(".comfyui-menu") || document.querySelector(".comfy-menu");
                if (menuGroup) {
                    const btn = createButton();
                    menuGroup.appendChild(btn);
                }
            }
        };

        // Small delay to ensure the DOM is fully constructed (especially in Vue)
        setTimeout(injectButton, 1000);
    },
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "Honda_LoadImage") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }
                const node = this;
                
                // Only apply defaults to newly created nodes (not when loading a workflow)
                // app.configuring_graph is true when a workflow is being loaded
                if (!app.configuring_graph) {
                    const lwWidget = node.widgets?.find(w => w.name === "lightweight_preview");
                    const maxResWidget = node.widgets?.find(w => w.name === "max_resolution");
                    
                    try {
                        const defaultLw = app.ui.settings.getSettingValue(SETTING_LIGHTWEIGHT, true);
                        const defaultRes = app.ui.settings.getSettingValue(SETTING_MAX_RES, 1024);
                        
                        if (lwWidget) lwWidget.value = defaultLw;
                        if (maxResWidget) maxResWidget.value = defaultRes;
                    } catch (e) {
                        console.warn("[Honda Nodes] Failed to apply default settings", e);
                    }
                }
            };
        }
    }
});
