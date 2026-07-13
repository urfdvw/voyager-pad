/**
 * Macro grammar validation.
 * Mirrors the firmware parsing: src/configure.py splits a macro on '~'
 * into hotkeys and each hotkey on '|' into codes (each stripped), then
 * src/macropad.py press_code/press_hotkey interprets the codes.
 */

// Returns null if `code` is a valid single key code, otherwise a reason.
function validateKeyCode(code) {
    if (KEYCODE_SET.has(code)) return null;
    if (MOUSE_MOVE_PATTERN.test(code)) return null;
    if (WAIT_PATTERN.test(code)) return null;
    if (code.startsWith('MOUSE_MOVE')) {
        return `'${code}' should be MOUSE_MOVE_X_Y_W with integers X, Y, W`;
    }
    if (code.startsWith('WAIT')) {
        return `'${code}' should be WAIT_MS with a whole number of milliseconds`;
    }
    return `'${code}' is not a supported key code`;
}

// Returns null if `macro` is valid, otherwise a reason string.
function validateMacro(macro) {
    for (const hotkey of macro.split('~')) {
        const codes = hotkey.split('|').map((code) => code.trim());
        if (codes.length === 1 && codes[0] === '') continue; // no-op hotkey
        if (codes[0].startsWith("'")) {
            // A quoted string is typed out as-is, but the firmware splits on
            // '~' and '|' before looking at quotes, so it must be one
            // self-contained code.
            if (codes.length > 1) {
                return `strings cannot contain '|': ${hotkey.trim()}`;
            }
            if (codes[0].length < 2 || !codes[0].endsWith("'")) {
                return `unclosed string: ${codes[0]} (strings cannot span '~' or '|')`;
            }
            continue;
        }
        for (const code of codes) {
            if (code === '') return `empty key in hotkey '${hotkey.trim()}'`;
            const reason = validateKeyCode(code);
            if (reason) return reason;
        }
    }
    return null;
}
