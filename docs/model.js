/**
 * settings.json data model.
 *
 * `data` mirrors the file: {"-1": {"<key>": [description, macro]}, ...}.
 * A top-level layer id 0-5 means that key is held down to switch to the
 * layer (src/macropad.py treats any key number found in the top level of
 * the configure dict as a layer switch), so a layer's key cannot carry
 * macros in any layer. Knob keys 6/7/8 are never layer switches here.
 */

const LAYER_KEY_NUMBERS = [0, 1, 2, 3, 4, 5]; // keys that can switch layers
const KNOB_KEY_NUMBERS = [6, 7, 8];           // knob press / turn right / turn left
const ALL_KEY_NUMBERS = [...LAYER_KEY_NUMBERS, ...KNOB_KEY_NUMBERS];

var data = null; // parsed settings.json contents

function reservedKeyNumbers() {
    return Object.keys(data).filter((id) => id !== '-1').map(Number);
}

function assignableKeyNumbers() {
    const reserved = reservedKeyNumbers();
    return ALL_KEY_NUMBERS.filter((key) => !reserved.includes(key));
}

function unusedLayerKeyNumbers() {
    return LAYER_KEY_NUMBERS.filter((key) => !(String(key) in data));
}

// Layer ids as strings, in numeric order ("-1" first).
function layerIds() {
    return Object.keys(data)
        .map(Number)
        .sort((a, b) => a - b)
        .map(String);
}

// True if any layer has a description or macro on this key.
function keyHasMacros(key) {
    return Object.values(data).some((layer) => {
        const entry = layer[String(key)];
        return Array.isArray(entry) && (entry[0] || entry[1]);
    });
}

/**
 * Keep layers and keys consistent: ensure the default layer exists, drop
 * layers that cannot be switched to, drop entries on reserved keys, and
 * fill every assignable key of every layer with ["", ""] placeholders
 * (the on-disk shape the firmware expects, see guides/configure.md).
 * Returns human-readable notes about any non-empty data that was dropped.
 */
function syncLayers() {
    const notes = [];
    if (!('-1' in data)) data['-1'] = {};
    for (const id of Object.keys(data)) {
        if (id === '-1') continue;
        if (!LAYER_KEY_NUMBERS.includes(Number(id))) {
            notes.push(`dropped layer '${id}' (layers can only be on keys 0-5)`);
            delete data[id];
        }
    }
    const assignable = assignableKeyNumbers();
    for (const id of Object.keys(data)) {
        const layer = data[id];
        for (const key of Object.keys(layer)) {
            const entry = layer[key];
            if (!assignable.includes(Number(key))
                && Array.isArray(entry) && (entry[0] || entry[1])) {
                notes.push(`dropped key ${key} of layer ${id} (key ${key} switches layers)`);
            }
        }
        const synced = {};
        for (const key of assignable) {
            const entry = Array.isArray(layer[String(key)]) ? layer[String(key)] : [];
            synced[String(key)] = [String(entry[0] ?? ''), String(entry[1] ?? '')];
        }
        data[id] = synced;
    }
    return notes;
}

function defaultData() {
    data = { '-1': {} };
    syncLayers();
}

function addLayer(key) {
    data[String(key)] = {};
    return syncLayers();
}

function removeLayer(key) {
    delete data[String(key)];
    return syncLayers();
}
