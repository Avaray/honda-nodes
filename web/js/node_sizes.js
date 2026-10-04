/**
 * HondaNodes.NodeSizes
 *
 * Central place to define default [width, height] for every Honda node.
 * Sizes are applied once when a node is first created; the user can still
 * resize freely afterwards (values are not locked).
 *
 * Format:  "NodeId": [width, height]
 */
import { app } from "../../../scripts/app.js";

const NODE_SIZES = {
    // ── Text ─────────────────────────────────────────────────────────────
    Honda_Text:             [340, 180],
    Honda_TextPreview:      [340, 200],
    Honda_TextConcatenate:  [340, 200],
    Honda_TextReplace:      [340, 260],
    Honda_TextSplit:        [340, 240],
    Honda_TextMatch:        [340, 200],
    Honda_TextSwitch:       [340, 160],
    Honda_TextCaseSwitch:   [380, 300],

    // ── JSON ─────────────────────────────────────────────────────────────
    Honda_JSONPreview:      [380, 220],
    Honda_JSONGetValue:     [340, 220],
    Honda_JSONSetKey:       [340, 260],
    Honda_JSONDeleteKey:    [340, 200],
    Honda_JSONMerge:        [340, 240],
    Honda_JSONValidate:     [340, 160],

    // ── File System ───────────────────────────────────────────────────────
    Honda_Directory:        [340, 120],
    Honda_CreateDirectory:  [340, 120],
    Honda_DeleteDirectory:  [340, 120],
    Honda_DeleteFile:       [340, 120],
    Honda_RenameFile:       [340, 140],
    Honda_MoveFile:         [340, 140],
    Honda_ReadFile:         [340, 120],
    Honda_ListFiles:        [340, 200],
    Honda_PathNormalize:    [340, 120],
    Honda_PathJoin:         [340, 240],

    // ── Image ─────────────────────────────────────────────────────────────
    Honda_LoadImage:        [280, 420],
    Honda_SaveImage:        [320, 500],
    Honda_PreviewImage:     [280, 420],
    Honda_WatermarkLoad:    [340, 200],
    Honda_WatermarkText:    [340, 260],

    // ── Metadata ──────────────────────────────────────────────────────────
    Honda_ExtractMetadata:  [480, 320],
    Honda_WriteMetadata:    [400, 220],
    Honda_ConvertMetadataFormat: [340, 160],
};

app.registerExtension({
    name: "HondaNodes.NodeSizes",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        const size = NODE_SIZES[nodeData.name];
        if (!size) return;

        const orig = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            orig?.apply(this, arguments);
            this.size = [...size];
            if (this.onResize) {
                this.onResize(this.size);
            }
        };
    },
});
