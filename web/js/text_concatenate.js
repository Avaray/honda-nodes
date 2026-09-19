import { app } from "../../../scripts/app.js";

/**
 * honda-nodes / Text Concatenate - auto-growing channel sockets (legacy V1 path only).
 *
 * When the running ComfyUI already supports the V3 schema, the Python side
 * registers the node through `comfy_api.latest` / `io.Autogrow`, which comes
 * with its own native socket auto-grow behaviour - this file does nothing
 * in that case.
 *
 * When ComfyUI falls back to the legacy V1 node, the Python side declares a
 * fixed pool of 99 optional, connection-only ("forceInput") STRING inputs
 * named text_1 .. text_99. This extension makes that pool behave like a
 * mixing console:
 *   - the node starts with exactly one empty channel socket.
 *   - connecting a wire to the last (empty) channel reveals a fresh empty
 *     channel right after it, up to 99 total.
 *   - disconnecting the trailing empty channel(s) removes them again, down
 *     to a single channel minimum. Disconnecting a channel in the middle
 *     just leaves it empty in place (its value is skipped by the node's
 *     own "skip_empty" option) rather than shifting anything around.
 *   - channel sockets are plain connections; there is nothing to type into
 *     them, they simply carry whatever STRING is wired into them.
 */

const NODE_TYPE = "Honda_TextConcatenate";
const MIN_FIELDS = 1;
const MAX_FIELDS = 99;
const CHANNEL_TYPE = "STRING";

function channelName(i) {
    return `Text Input ${String(i).padStart(2, '0')}`;
}

function isHondaNode(node) {
    return !!(node.inputs && node.inputs.some((inp) => inp.name === channelName(1)));
}

function relabelChannels(node) {
    node.inputs.forEach((inp, idx) => {
        // Best-effort nicer display; falls back harmlessly to `text_N` on
        // frontends that don't read a separate slot label.
        inp.label = `#${idx + 1}`;
    });
}

/**
 * Ensure exactly one empty trailing channel exists right after the
 * highest currently-connected channel (or MIN_FIELDS channels if nothing
 * is connected yet), clamped to MAX_FIELDS. Never touches a connected
 * channel.
 */
function normalizeChannels(node) {
    let highestConnected = -1;
    node.inputs.forEach((inp, idx) => {
        if (inp.link != null) highestConnected = idx;
    });

    const desiredCount = Math.min(MAX_FIELDS, Math.max(MIN_FIELDS, highestConnected + 2));

    while (node.inputs.length < desiredCount) {
        const nextIndex = node.inputs.length + 1;
        node.addInput(channelName(nextIndex), CHANNEL_TYPE);
    }
    while (
        node.inputs.length > desiredCount &&
        node.inputs[node.inputs.length - 1].link == null
    ) {
        node.removeInput(node.inputs.length - 1);
    }

    relabelChannels(node);
    node.setSize(node.computeSize());
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "honda.nodes.textConcatenate",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_TYPE) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            const node = this;

            if (node.honda_tc_ready) return result;
            // If there's no "text_1" input, we're actually running against
            // the V3/Autogrow node (same node_id, different backend) - it
            // already grows its own sockets natively, so do nothing here.
            if (!isHondaNode(node)) return result;
            node.honda_tc_ready = true;

            normalizeChannels(node);
            return result;
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (type, slotIndex, isConnected, linkInfo, ioSlot) {
            const result = onConnectionsChange
                ? onConnectionsChange.apply(this, arguments)
                : undefined;
            const node = this;
            if (node.honda_tc_ready && type === LiteGraph.INPUT) {
                normalizeChannels(node);
            }
            return result;
        };

        // When a saved workflow is loaded, the node is first constructed
        // fresh (triggering onNodeCreated -> trimmed to MIN_FIELDS), and
        // only afterwards is the saved snapshot applied via onConfigure.
        // Grow the channel pool back out to match the incoming snapshot
        // *before* the base configure logic runs, so its saved links land
        // on the right sockets instead of being silently dropped.
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (info) {
            const node = this;
            if (node.honda_tc_ready && info && Array.isArray(info.inputs)) {
                while (node.inputs.length < info.inputs.length && node.inputs.length < MAX_FIELDS) {
                    const nextIndex = node.inputs.length + 1;
                    node.addInput(channelName(nextIndex), CHANNEL_TYPE);
                }
            }
            const result = onConfigure ? onConfigure.apply(this, arguments) : undefined;
            if (node.honda_tc_ready) {
                normalizeChannels(node);
            }
            return result;
        };
    },
});
