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
    Honda_Text:             [340, 180],  // single multiline input
    Honda_TextPreview:      [340, 200],  // multiline input + DOM preview widget
    Honda_TextConcatenate:  [340, 200],  // 2 inputs + separator combo
    Honda_TextReplace:      [340, 260],  // 3 string inputs + 3 bool toggles
    Honda_TextSplit:        [340, 240],  // 2 combos + 2 string + 2 bool
    Honda_TextMatch:        [340, 200],  // 2 string inputs + 2 bool toggles
    Honda_TextSwitch:       [340, 160],  // condition bool + 2 string inputs
    Honda_TextCaseSwitch:   [380, 300],  // condition + 2 multiline + default + 2 bools

    // ── JSON ─────────────────────────────────────────────────────────────
    Honda_JSONPreview:      [380, 220],  // multiline input + DOM preview widget
    Honda_JSONGetValue:     [340, 220],  // multiline + key + bool
    Honda_JSONSetKey:       [340, 260],  // multiline + key + value (multiline) + bool
    Honda_JSONDeleteKey:    [340, 200],  // multiline + key
    Honda_JSONMerge:        [340, 240],  // 2 multiline inputs
    Honda_JSONValidate:     [340, 160],  // multiline input → bool output

    // ── File System ───────────────────────────────────────────────────────
    Honda_Directory:        [340, 120],  // single path input
    Honda_CreateDirectory:  [340, 120],
    Honda_DeleteDirectory:  [340, 120],
    Honda_DeleteFile:       [340, 120],
    Honda_RenameFile:       [340, 140],  // source + new name
    Honda_MoveFile:         [340, 140],  // source + destination
    Honda_ReadFile:         [340, 120],
    Honda_ListFiles:        [340, 200],  // path + recursive bool + limit + filter
    Honda_PathNormalize:    [340, 120],  // single path input → normalized output
    Honda_PathJoin:         [340, 240],  // up to 5 segments

    // ── Image ─────────────────────────────────────────────────────────────
    Honda_LoadImage:        [340, 160],  // combo picker + 4 outputs
    Honda_SaveImage:        [340, 200],  // image + 3 string inputs

    // ── Metadata ──────────────────────────────────────────────────────────
    Honda_ExtractMetadata:  [480, 320],  // path input + large DOM preview
    Honda_WriteMetadata:    [400, 220],  // path + multiline JSON + optional output
};

app.registerExtension({
    name: "HondaNodes.NodeSizes",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        const size = NODE_SIZES[nodeData.name];
        if (!size) return;

        const orig = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            orig?.apply(this, arguments);
            this.size = [...size]; // spread so each instance gets its own array
        };
    },
});
