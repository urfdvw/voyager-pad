/**
 * IME-style autocomplete for macro inputs.
 *
 * While typing, the '~'/'|'-delimited token under the caret is matched
 * against KEYCODES and shown in a dropdown below the input.
 * ArrowUp/ArrowDown move the highlight (wrapping), Enter or Tab inserts
 * the highlighted code in place of the token, Escape closes the dropdown,
 * and any other editing just live-updates the list.
 */

let acInput = null;   // input the dropdown is currently attached to
let acMatches = [];
let acIndex = 0;
let acStart = 0;      // token range in the input value, replaced on accept
let acEnd = 0;
let acSuppress = false;

const acList = document.createElement('ul');
acList.id = 'autocomplete';
acList.hidden = true;
document.body.appendChild(acList);

function attachAutocomplete(input) {
    input.addEventListener('input', () => updateAutocomplete(input));
    input.addEventListener('click', () => updateAutocomplete(input));
    input.addEventListener('keydown', (event) => autocompleteKeydown(input, event));
    input.addEventListener('blur', closeAutocomplete);
}

// The '~'/'|'-delimited token around the caret.
function tokenRange(input) {
    const value = input.value;
    const caret = input.selectionStart;
    let start = caret;
    while (start > 0 && !'~|'.includes(value[start - 1])) start -= 1;
    let end = caret;
    while (end < value.length && !'~|'.includes(value[end])) end += 1;
    return { start, end, token: value.slice(start, end).trim() };
}

function updateAutocomplete(input) {
    if (acSuppress) {
        acSuppress = false;
        return;
    }
    const { start, end, token } = tokenRange(input);
    if (token === '' || token.startsWith("'")) {
        closeAutocomplete();
        return;
    }
    const upper = token.toUpperCase();
    const prefix = KEYCODES.filter((code) => code.startsWith(upper));
    const inner = KEYCODES.filter(
        (code) => !code.startsWith(upper) && code.includes(upper)
    );
    const matches = [...prefix, ...inner];
    if (matches.length === 0 || (matches.length === 1 && matches[0] === token)) {
        closeAutocomplete();
        return;
    }
    acInput = input;
    acMatches = matches;
    acIndex = 0;
    acStart = start;
    acEnd = end;
    renderAutocomplete();
}

function renderAutocomplete() {
    acList.innerHTML = '';
    acMatches.forEach((code, i) => {
        const item = document.createElement('li');
        item.textContent = code;
        if (i === acIndex) item.classList.add('selected');
        item.addEventListener('mousedown', (event) => {
            event.preventDefault(); // keep focus (and blur handler) off
            acIndex = i;
            acceptAutocomplete();
        });
        acList.appendChild(item);
    });
    const rect = acInput.getBoundingClientRect();
    acList.style.left = `${rect.left + window.scrollX}px`;
    acList.style.top = `${rect.bottom + window.scrollY + 2}px`;
    acList.style.minWidth = `${rect.width / 2}px`;
    acList.hidden = false;
    acList.children[acIndex]?.scrollIntoView({ block: 'nearest' });
}

function acceptAutocomplete() {
    const input = acInput;
    const code = acMatches[acIndex];
    const value = input.value;
    input.value = value.slice(0, acStart) + code + value.slice(acEnd);
    const caret = acStart + code.length;
    input.setSelectionRange(caret, caret);
    closeAutocomplete();
    // Notify app.js (model update + validation) without reopening the list.
    acSuppress = true;
    input.dispatchEvent(new Event('input', { bubbles: true }));
}

function autocompleteKeydown(input, event) {
    if (acList.hidden || acInput !== input) return;
    if (event.key === 'ArrowDown') {
        acIndex = (acIndex + 1) % acMatches.length;
        renderAutocomplete();
        event.preventDefault();
    } else if (event.key === 'ArrowUp') {
        acIndex = (acIndex + acMatches.length - 1) % acMatches.length;
        renderAutocomplete();
        event.preventDefault();
    } else if (event.key === 'Enter' || event.key === 'Tab') {
        acceptAutocomplete();
        event.preventDefault();
    } else if (event.key === 'Escape') {
        closeAutocomplete();
        event.preventDefault();
    } else if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
        // Caret is moving away from the token the list was built for.
        closeAutocomplete();
    }
}

function closeAutocomplete() {
    acList.hidden = true;
    acInput = null;
    acMatches = [];
}
