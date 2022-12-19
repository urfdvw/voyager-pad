import displayio
from terminalio import FONT
from adafruit_display_text.label import Label
from adafruit_display_text.scrolling_label import ScrollingLabel
from adafruit_display_text import wrap_text_to_lines

class MacroPadDisplay:
    def __init__(self, configure):
        self.configure = configure
        self.layer_text = {
            layer: '\n'.join(wrap_text_to_lines(
                ' '.join([
                    str(key_number) + ':' + configure[layer][key_number][0]
                    for key_number in sorted(configure[layer].keys())
                    if configure[layer][key_number][0]
                ])
            , 128 // 6))
            for layer in configure
        }
        self.layer = -1
    def show_layer(self, layer):
        raise NotImplementedError
    def show_macro(self, key_number):
        raise NotImplementedError
    
class MONO_128x32(MacroPadDisplay):
    def __init__(self, configure, display):
        super().__init__(configure)
        # print(self.layer_text)
        self.display = display
        self.splash = displayio.Group()
        self.display.show(self.splash)
        
        self.layer_group = displayio.Group()
        self.splash.append(self.layer_group)
        self.layer_group.hidden = False
        self.layer_lable = Label(
            FONT,
            text=self.layer_text[self.layer],
            color=0xFFFFFF,
            background_color=0x000000,
            anchor_point=(0, 0),
            x=0, y=7,
            scale=1,
            line_spacing=0.8
        )
        self.layer_group.append(self.layer_lable)
        
        self.macro_group = displayio.Group()
        self.splash.append(self.macro_group)
        self.macro_group.hidden = True
        self.macro_lable = Label(
            FONT,
            text='',
            color=0xFFFFFF,
            background_color=0x000000,
            x=0, y=15,
            scale=2
        )
        self.macro_group.append(self.macro_lable)
        
    def show_layer(self, layer):
        self.layer_lable.text = self.layer_text[layer]
        self.layer_group.hidden = False
        self.macro_group.hidden = True
        
    def show_macro(self, key_number):
        self.macro_lable.text = self.configure[self.layer][key_number][0]
        self.layer_group.hidden = True
        self.macro_group.hidden = False
        
    
    
# main -----------------
import board
import displayio
import adafruit_displayio_ssd1306
from configure import configure

displayio.release_displays()

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

disp = MONO_128x32(configure, display)
disp.show_macro(2)
while True:
    pass