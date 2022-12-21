import board
import busio
import usb_hid
import configure
import displayio
import adafruit_displayio_ssd1306

from macropad import MacroKeyPad, MONO_128x32, MacroPad

# define display
displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA, frequency=int(1e6))
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
macropaddisp = MONO_128x32(configure, display)
# define keypad
macrokeypad = MacroKeyPad(
    key_pins=(
        board.D10, # lower row
        board.D6,
        board.D3, # upper row
        board.D2,
        board.D1,
        board.D0,
        board.D9, # nob
    ),
    encoder_pins=(
        board.D8, # A
        board.D7, # B
    )
)
# define macropad
macropad = MacroPad(
    macrokeypad=macrokeypad,
    configure=configure,
    hid=usb_hid,
    macropaddisp=macropaddisp,
)

while True:
    macropad()