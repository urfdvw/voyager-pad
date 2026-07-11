# Circuit / Pin Connections

This document describes the physical wiring expected by `code.py` /
`macropad.py` on the **Seeeduino XIAO RP2040** board (board id
`seeeduino_xiao_rp2040`, see `boot_out.txt`).

The XIAO RP2040 silkscreen labels some pins differently from the
CircuitPython `board.*` names used in this code. The table below gives
both.

## OLED Display (SSD1306, 128x32, I2C)

Driven by `adafruit_displayio_ssd1306` over I2C at address `0x3C`,
1 MHz bus speed (see `code.py`).

| Display pin | Connects to (code) | XIAO silkscreen |
|---|---|---|
| SDA | `board.SDA` | SDA |
| SCL | `board.SCL` | SCL |
| VCC | 3.3V | 3V3 |
| GND | GND | GND |

## Macro keys (7 tactile switches)

Each switch wires one leg to the listed pin and the other leg to GND.
Firmware enables an internal pull-up and treats the key as pressed when
the pin reads low (`pull=True, value_when_pressed=False` in
`MacroKeyPad`), so no external resistors are needed.

| key_number | code pin | XIAO silkscreen | Role (from `macropad.py` / `settings.json`) |
|---|---|---|---|
| 0 | `board.D10` | MOSI | Lower row, key 1 — hold to select layer 0 |
| 1 | `board.D6` | TX | Lower row, key 2 — hold to select layer 1 |
| 2 | `board.D3` | A3 | Upper row, key 1 — macro key |
| 3 | `board.D2` | A2 | Upper row, key 2 — macro key |
| 4 | `board.D1` | A1 | Upper row, key 3 — macro key |
| 5 | `board.D0` | A0 | Upper row, key 4 — macro key |
| 6 | `board.D9` | MISO | Rotary encoder push button ("nob") — macro key |

Note: the "lower row" / "upper row" grouping above comes from the
inline comments in `code.py`; wire the physical rows to match your own
enclosure if it differs.

Layer 0 and layer 1 (key_number 0 and 1) are momentary: holding them
switches to that layer, releasing returns to the default layer (`-1`).
Key numbers 2–6 emit whatever macro is configured in `settings.json`
for the currently active layer.

## Rotary encoder

A quadrature rotary encoder provides scroll/volume-style input, decoded
by `rotaryio.IncrementalEncoder`. Its push button is wired as key 6
above (shared with the macro key matrix, not a separate input).

| Encoder pin | code pin | XIAO silkscreen |
|---|---|---|
| A | `board.D8` | SCK |
| B | `board.D7` | RX |
| Push button | `board.D9` | MISO (see key_number 6 above) |

Rotation does not use extra physical pins beyond A/B: clockwise steps
are reported by software as virtual `key_number 7`, counter-clockwise
steps as virtual `key_number 8` (see `MacroKeyPad.events` in
`macropad.py`). These correspond to the `"7"` and `"8"` macro entries
in `settings.json`.

## USB

The board connects to the host over USB for both power and the
keyboard/mouse/consumer-control HID interface (see `boot.py`).
