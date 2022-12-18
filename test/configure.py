"""
| press at the same time,
~ press in sequence
'' type out as is
"""

configure = {
    -1: { # without modifier
        2: "ALT", # upper row
        3: "GUI|V",
        4: "GUI|A~GUI|C",
        5: "'Hello, World!'",
        6: "PLAY_PAUSE", # nob
        7: "VOLUME_INCREMENT", # clock
        8: "VOLUME_DECREMENT", # counterclock
    },
    0: { # with modifier
        2: "'hi level0'", # upper row
        3: "LEFT_BUTTON",
        4: "MIDDLE_BUTTON",
        5: "RIGHT_BUTTON",
        6: "", # nob
        7: "", # clock
        8: "", # counterclock
    },
    1: { # with modifier
        2: "'hi level1'", # upper row
        3: "",
        4: "",
        5: "",
        6: "", # nob
        7: "", # clock
        8: "", # counterclock
    },
}

sequence = {
    layer: { 
        key_number: [
            [key.strip() for key in sec.split('|')]
            for sec 
            in configure[layer][key_number].split('~')
        ]
        for key_number in configure[layer]
    }
    for layer in configure
}

"""
TODO: check the configuration

available configure keys

keyboard:
A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, ZERO, ENTER, RETURN, ESCAPE, BACKSPACE, TAB, SPACEBAR, SPACE, MINUS, EQUALS, LEFT_BRACKET, RIGHT_BRACKET, BACKSLASH, POUND, SEMICOLON, QUOTE, GRAVE_ACCENT, COMMA, PERIOD, FORWARD_SLASH, CAPS_LOCK, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, PRINT_SCREEN, SCROLL_LOCK, PAUSE, INSERT, HOME, PAGE_UP, DELETE, END, PAGE_DOWN, RIGHT_ARROW, LEFT_ARROW, DOWN_ARROW, UP_ARROW, KEYPAD_NUMLOCK, KEYPAD_FORWARD_SLASH, KEYPAD_ASTERISK, KEYPAD_MINUS, KEYPAD_PLUS, KEYPAD_ENTER, KEYPAD_ONE, KEYPAD_TWO, KEYPAD_THREE, KEYPAD_FOUR, KEYPAD_FIVE, KEYPAD_SIX, KEYPAD_SEVEN, KEYPAD_EIGHT, KEYPAD_NINE, KEYPAD_ZERO, KEYPAD_PERIOD, KEYPAD_BACKSLASH, APPLICATION, POWER, KEYPAD_EQUALS, F13, F14, F15, F16, F17, F18, F19, F20, F21, F22, F23, F24, LEFT_CONTROL, CONTROL, LEFT_SHIFT, SHIFT, LEFT_ALT, ALT, OPTION, LEFT_GUI, GUI, WINDOWS, COMMAND, RIGHT_CONTROL, RIGHT_SHIFT, RIGHT_ALT, RIGHT_GUI
mediacontroll
RECORD, FAST_FORWARD, REWIND, SCAN_NEXT_TRACK, SCAN_PREVIOUS_TRACK, STOP, EJECT, PLAY_PAUSE, MUTE, VOLUME_DECREMENT, VOLUME_INCREMENT, BRIGHTNESS_DECREMENT, BRIGHTNESS_INCREMENT
mouse
RIGHT_BUTTON, LEFT_BUTTON, MIDDLE_BUTTON
"""