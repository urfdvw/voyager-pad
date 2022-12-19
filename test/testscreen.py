# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid white
background, a smaller black rectangle, and some white text.
"""

import board
import displayio
from terminalio import FONT
from adafruit_display_text import label
from adafruit_display_text.scrolling_label import ScrollingLabel
import adafruit_displayio_ssd1306

displayio.release_displays()

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

# Make the display context
splash = displayio.Group()
display.show(splash)

# Draw a smaller inner rectangle
color_bitmap = displayio.Bitmap(128, 32, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a label
text = "HelloWorld!"
text_area = ScrollingLabel(FONT, text=text, color=0xFFFFFF, background_color=0x000000, x=0, y=15, max_characters=4, animate_time=0.3, scale=2)
splash.append(text_area)

while True:
    text_area.update()
