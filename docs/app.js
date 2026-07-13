/**
 * Page logic: layer tabs, key table, folder open/save, status line.
 */

let fileHandle = null;
let folderName = '';
let dirty = false;
let currentLayer = '-1';

const openButton = document.getElementById('open-folder');
const saveButton = document.getElementById('save');
const statusLine = document.getElementById('status');
const tabBar = document.getElementById('layer-tabs');
const editor = document.getElementById('editor');
const placeholder = document.getElementById('placeholder');

const KEY_LABELS = { 6: 'knob press', 7: 'knob right', 8: 'knob left' };

function setStatus(message, kind = '') {
    statusLine.textContent = message;
    statusLine.className = 'status' + (kind ? ' ' + kind : '');
}

function markDirty() {
    if (!dirty) {
        dirty = true;
        setStatus('Unsaved changes');
    }
}

function showEditor(show) {
    tabBar.hidden = !show;
    placeholder.hidden = show;
    saveButton.disabled = !show;
    if (!show) editor.innerHTML = '';
}

/**
 * Rendering ******************************************************
 */

function render() {
    renderTabs();
    renderTable();
}

function renderTabs() {
    tabBar.innerHTML = '';
    for (const id of layerIds()) {
        const tab = document.createElement('button');
        tab.className = 'tab' + (id === currentLayer ? ' active' : '');
        tab.textContent = id === '-1' ? 'Default layer' : `Layer on key ${id}`;
        tab.addEventListener('click', () => {
            currentLayer = id;
            render();
        });
        tabBar.appendChild(tab);
    }
    if (unusedLayerKeyNumbers().length > 0) {
        const add = document.createElement('button');
        add.className = 'tab add';
        add.textContent = '+ Add layer';
        add.addEventListener('click', addLayerClicked);
        tabBar.appendChild(add);
    }
    if (currentLayer !== '-1') {
        const remove = document.createElement('button');
        remove.className = 'tab remove';
        remove.textContent = 'Remove this layer';
        remove.addEventListener('click', removeLayerClicked);
        tabBar.appendChild(remove);
    }
}

function addLayerClicked(event) {
    const existing = document.getElementById('add-layer-menu');
    if (existing) {
        existing.remove();
        return;
    }
    const menu = document.createElement('div');
    menu.id = 'add-layer-menu';
    menu.className = 'menu';
    for (const key of unusedLayerKeyNumbers()) {
        const item = document.createElement('button');
        const clears = keyHasMacros(key);
        item.textContent = `Hold key ${key}` + (clears ? ' — clears its macros' : '');
        item.addEventListener('click', () => {
            menu.remove();
            if (clears && !window.confirm(
                `Key ${key} will become the switch of the new layer.\n`
                + `Its existing macros in ALL layers will be removed. Continue?`
            )) return;
            addLayer(key);
            currentLayer = String(key);
            markDirty();
            render();
        });
        menu.appendChild(item);
    }
    const rect = event.currentTarget.getBoundingClientRect();
    menu.style.left = `${rect.left + window.scrollX}px`;
    menu.style.top = `${rect.bottom + window.scrollY + 4}px`;
    document.body.appendChild(menu);
    setTimeout(() => {
        document.addEventListener('click', () => menu.remove(), { once: true });
    });
}

function removeLayerClicked() {
    if (!window.confirm(
        `Remove the layer on key ${currentLayer}?\n`
        + `Its macros will be lost and key ${currentLayer} becomes assignable again.`
    )) return;
    removeLayer(Number(currentLayer));
    currentLayer = '-1';
    markDirty();
    render();
}

function renderTable() {
    editor.innerHTML = '';
    const table = document.createElement('table');

    const head = table.createTHead().insertRow();
    for (const title of ['Key', 'Name', 'Macro']) {
        const cell = document.createElement('th');
        cell.textContent = title;
        head.appendChild(cell);
    }

    const body = table.createTBody();
    for (const key of assignableKeyNumbers()) {
        const entry = data[currentLayer][String(key)];
        const row = body.insertRow();

        const keyCell = row.insertCell();
        keyCell.className = 'key';
        keyCell.textContent = key;
        if (KEY_LABELS[key]) {
            const label = document.createElement('small');
            label.textContent = KEY_LABELS[key];
            keyCell.appendChild(label);
        }

        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.className = 'name';
        nameInput.placeholder = 'shown on the screen';
        nameInput.value = entry[0];
        nameInput.addEventListener('input', () => {
            entry[0] = nameInput.value;
            markDirty();
        });
        row.insertCell().appendChild(nameInput);

        const macroInput = document.createElement('input');
        macroInput.type = 'text';
        macroInput.className = 'macro';
        macroInput.placeholder = "e.g. CONTROL|C or 'hello'~ENTER";
        macroInput.value = entry[1];
        macroInput.addEventListener('input', () => {
            entry[1] = macroInput.value;
            validateField(macroInput);
            markDirty();
        });
        attachAutocomplete(macroInput);
        validateField(macroInput);
        row.insertCell().appendChild(macroInput);
    }
    editor.appendChild(table);
}

function validateField(input) {
    const reason = validateMacro(input.value);
    input.classList.toggle('invalid', reason !== null);
    input.title = reason ?? '';
    return reason;
}

/**
 * Open / save ****************************************************
 */

async function writeData() {
    const writable = await fileHandle.createWritable();
    await writable.write(JSON.stringify(data, null, 2));
    await writable.close();
}

async function openClicked() {
    let directory;
    try {
        directory = await window.showDirectoryPicker({ mode: 'readwrite' });
    } catch {
        return; // picker cancelled
    }
    try {
        folderName = directory.name;
        fileHandle = await directory.getFileHandle('settings.json', { create: true });
        const text = await (await fileHandle.getFile()).text();
        let notes = [];
        if (text.trim() === '') {
            defaultData();
            await writeData();
            setStatus(`Created a new settings.json in '${folderName}'`, 'ok');
        } else {
            let parsed;
            try {
                parsed = JSON.parse(text);
            } catch (error) {
                parsed = null;
            }
            if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
                fileHandle = null;
                data = null;
                showEditor(false);
                setStatus(
                    `'${folderName}/settings.json' is not a valid settings file `
                    + '— fix or delete it, then open the folder again.', 'error'
                );
                return;
            }
            data = parsed;
            notes = syncLayers();
            if (notes.length > 0) {
                setStatus(`Opened '${folderName}/settings.json' — ${notes.join('; ')}. Save to apply.`);
            } else {
                setStatus(`Opened '${folderName}/settings.json'`, 'ok');
            }
        }
        currentLayer = '-1';
        dirty = notes.length > 0;
        showEditor(true);
        render();
    } catch (error) {
        fileHandle = null;
        data = null;
        showEditor(false);
        setStatus(`Could not open settings.json: ${error.message}`, 'error');
    }
}

async function saveClicked() {
    if (!fileHandle) return;
    const problems = [];
    for (const id of layerIds()) {
        for (const [key, entry] of Object.entries(data[id])) {
            const reason = validateMacro(entry[1]);
            if (reason) problems.push(`layer ${id} key ${key}: ${reason}`);
        }
    }
    if (problems.length > 0) {
        const more = problems.length > 1 ? ` (+${problems.length - 1} more)` : '';
        setStatus(`Cannot save — ${problems[0]}${more}`, 'error');
        return;
    }
    try {
        await writeData();
        dirty = false;
        setStatus(`Saved to '${folderName}/settings.json' at ${new Date().toLocaleTimeString()}`, 'ok');
    } catch (error) {
        setStatus(`Save failed: ${error.message}`, 'error');
    }
}

/**
 * Init ***********************************************************
 */

if (window.showDirectoryPicker) {
    openButton.addEventListener('click', openClicked);
    saveButton.addEventListener('click', saveClicked);
    setStatus("Open the device's CIRCUITPY drive to start.");
} else {
    openButton.disabled = true;
    setStatus('This page needs the File System Access API — please use Chrome or Edge.', 'error');
}

document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        if (!saveButton.disabled) saveClicked();
    }
});

window.addEventListener('beforeunload', (event) => {
    if (dirty) event.preventDefault();
});
