
# Configure

## How to configure the macros on the device
1. Connect the Voyager Pad to computer by USB cable. It will show up as a drive called 'CIRCUITPY'.
2. Open [this page](https://urfdvw.github.io/voyager-pad/): https://urfdvw.github.io/voyager-pad/
    - Or open 'Set Macro.url' on the 'CIRCUITPY' drive.
3. In the opened web page, click on `Open 'settings.json'`.
4. Find the 'settings.json' file on the 'CIRCUITPY' drive and open.
5. Change the names and macros in the web page.
6. Click on 'save' in the web page to save changes to the device.
 
## Macro terminologies and gramma
- key: a key stroke
- hotkey: a combination of keys to be send together
    - `|` is used to combine keys in the hotkeys
- macro: a set of hotkeys to be send in a sequence
    - `~` is used to combine hotkeys in the macro
- string: a string to be typed out as-is (US keyboard)
    - `''` are used to indicate strings
    - a string is considered as special hotkey

## Supported macro keys
### Keyboard keys
A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, ZERO, ENTER, RETURN, ESCAPE, BACKSPACE, TAB, SPACEBAR, SPACE, MINUS, EQUALS, LEFT_BRACKET, RIGHT_BRACKET, BACKSLASH, POUND, SEMICOLON, QUOTE, GRAVE_ACCENT, COMMA, PERIOD, FORWARD_SLASH, CAPS_LOCK, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, PRINT_SCREEN, SCROLL_LOCK, PAUSE, INSERT, HOME, PAGE_UP, DELETE, END, PAGE_DOWN, RIGHT_ARROW, LEFT_ARROW, DOWN_ARROW, UP_ARROW, KEYPAD_NUMLOCK, KEYPAD_FORWARD_SLASH, KEYPAD_ASTERISK, KEYPAD_MINUS, KEYPAD_PLUS, KEYPAD_ENTER, KEYPAD_ONE, KEYPAD_TWO, KEYPAD_THREE, KEYPAD_FOUR, KEYPAD_FIVE, KEYPAD_SIX, KEYPAD_SEVEN, KEYPAD_EIGHT, KEYPAD_NINE, KEYPAD_ZERO, KEYPAD_PERIOD, KEYPAD_BACKSLASH, APPLICATION, POWER, KEYPAD_EQUALS, F13, F14, F15, F16, F17, F18, F19, F20, F21, F22, F23, F24, LEFT_CONTROL, CONTROL, LEFT_SHIFT, SHIFT, LEFT_ALT, ALT, OPTION, LEFT_GUI, GUI, WINDOWS, COMMAND, RIGHT_CONTROL, RIGHT_SHIFT, RIGHT_ALT, RIGHT_GUI
### Media control keys
RECORD, FAST_FORWARD, REWIND, SCAN_NEXT_TRACK, SCAN_PREVIOUS_TRACK, STOP, EJECT, PLAY_PAUSE, MUTE, VOLUME_DECREMENT, VOLUME_INCREMENT, BRIGHTNESS_DECREMENT, BRIGHTNESS_INCREMENT
### Mouse
RIGHT_BUTTON, LEFT_BUTTON, MIDDLE_BUTTON

MOUSE_MOVE_X_Y_W (*Replace `X`, `Y` and `W` with integers representing the move of x-axis, y-axis and scroll wheel*)
### Gamepad
GAMEPAD_BUTTON_N (*REPLACE `N` with button number, within and include 1 to 16*)

JOY_SET_X_Y_Z_RZ, 
JOY_ALTER_X_Y_Z_RZ (*Replace `X`, `Y`, `Z` and `RZ` with integers representing the move of corresponding joystick, within and include -127 to 127*, but not all zeros),
JOY_CENTER
### Special (No USB action related)
WAIT_MS (
    since firmware v1.0.1 
    *REPLACE `MS` with an integer reperesenting how many milliseconds to wait*
)

## Macro Examples
- `ALT`: use the key as alt key
- `CONTROL|V`: send Ctrl and V key at the same time
- `CONTROL|A~CONTROL|C`: send Ctrl and A together and then send Ctrl and C together
- `'Hello, World!'`: Type the string out as-is
- `SHIFT|MOUSE_MOVE_0_0_3`: Hold shift and scroll up(down depends on your system) by 3 lines, no cursor move.

see the source code for detailed ['settings.json' examples](https://github.com/urfdvw/voyager-pad/tree/main/example%20settings)

## Raw setting format
All macro configurations are in file `settings.json` with format
```json
{
    "KEY_NUMBER_OF_LAYER_KEY": {
        "KEY_NUMBER": [
            "SHORT_DESCRIPTION", 
            "MACRO"
        ],
        ...
    },
    ...
}
```

Note:
- The default layer number is `-1`, which is not associated with any key number.
- You can use any key as layer modifier.
- SHORT_DESCRIPTION are displayed on the OLED.
- If there is no description or macro, use `""` as space holder.