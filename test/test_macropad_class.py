# cpy native
import rotaryio
import keypad

class EventQueue:
    def __init__(self):
        self.data = []

    def append(self, given):
        self.data.append(given)

    def get(self):
        if self.data:
            return self.data.pop(0)
        else:
            return None

    def clear(self):
        self.data = []

    def __len__(self):
        return len(self.data)

    def __bool__(self):
        return bool(self.data)
        
class MacroKeyPad:
    def __init__(self, key_pins, encoder_pins):
        # hardware
        self.encoder=rotaryio.IncrementalEncoder(*encoder_pins)
        self.keys = keypad.Keys(
            key_pins, 
            pull=True,
            value_when_pressed=False
        )
        self.n_keys = len(key_pins)
        # queue
        self._events = EventQueue()
        
    @property
    def events(self):
        position = self.encoder.position
        if position != 0:
            key_number = self.n_keys if position > 0 else self.n_keys + 1
            position = abs(position)
            for i in range(position):
                self._events.append(
                    keypad.Event(
                        key_number=key_number,
                        pressed=True,
                    )
                )
                self._events.append(
                    keypad.Event(
                        key_number=key_number,
                        pressed=False,
                    )
                )
            self.encoder.position = 0
                
        while event := self.keys.events.get():
            self._events.append(event)
        return self._events


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
        self.state = 0
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
        text = self.layer_text[layer]
        if (self.layer_lable.text == text 
        and self.state == 0):
            return
        self.state = 0
        self.layer = layer
        self.layer_lable.text = text
        self.layer_group.hidden = False
        self.macro_group.hidden = True
        
    def show_macro(self, key_number):
        text = self.configure[self.layer][key_number][0]
        if (self.macro_lable.text == text
        and self.state == 1):
            return
        self.state = 1
        self.macro_lable.text = text
        self.layer_group.hidden = True
        self.macro_group.hidden = False
        

from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.mouse import Mouse

class MacroPad:
    def __init__(
        self,
        macrokeypad,
        macropaddisp,
        configure,
        hid,
    ):
        self.macrokeypad = macrokeypad
        self.macropaddisp = macropaddisp
        self.configure = configure
        
        self.layer = -1
        self.n_layer_key_press = 0
        self.n_key_press = 0
        
        
        self.keyboard = Keyboard(hid.devices)
        self.keyboard_layout = KeyboardLayoutUS(self.keyboard)
        self.consumer_control = ConsumerControl(hid.devices)
        self.mouse = Mouse(hid.devices)
    
    def press_code(self, code):
        if code in Keycode.__dict__:
            self.keyboard.press(Keycode.__dict__[code])
        elif code in ConsumerControlCode.__dict__:
            self.consumer_control.press(ConsumerControlCode.__dict__[code])
        elif code in Mouse.__dict__:
            self.mouse.press(Mouse.__dict__[code])
        elif code.startswith('MOUSE_MOVE'):
            x, y, w = [int(hotkey) for hotkey in code.split('_')[-3:]]
            self.mouse.move(x=x,y=y,wheel=w)
            
    def release_code(self, code):
        if code in Keycode.__dict__:
            self.keyboard.release(Keycode.__dict__[code])
        elif code in ConsumerControlCode.__dict__:
            self.consumer_control.release()
        elif code in Mouse.__dict__:
            self.mouse.release(Mouse.__dict__[code])
            
    def press_hotkey(self, hotkey):
        if len(hotkey[0]) == 0:
            return
        if hotkey[0][0] == "'":
            return
        else:
            for code in hotkey:
                self.press_code(code)
            
    def release_hotkey(self, hotkey):
        if len(hotkey[0]) == 0:
            return
        if hotkey[0][0] == "'":
            self.keyboard_layout.write(hotkey[0][1:-1])
        else:
            for code in hotkey:
                self.release_code(code)
            
    
    def __call__(self):
        # get event
        event = self.macrokeypad.events.get()
        if event is None:
            return
        # count press
        self.n_key_press += 1 if event.pressed else -1
        if event.key_number in self.configure.configure:
            self.n_layer_key_press += 1 if event.pressed else -1
        # get layer
        if event.key_number in self.configure.configure:
            if event.pressed:
                self.layer = event.key_number
                self.macropaddisp.show_layer(self.layer)
            if self.n_layer_key_press == 0:
                self.layer = -1
                self.macropaddisp.show_layer(self.layer)
        # get macro
        else:
            macro = self.configure.macro[self.layer][event.key_number]
            
            # print(macro)
            if event.pressed:
                for i in range(len(macro)):
                    self.press_hotkey(macro[i])
                    if i != len(macro) - 1:
                        self.release_hotkey(macro[i])
                self.macropaddisp.show_macro(event.key_number)
            else:
                self.release_hotkey(macro[-1])
                self.macropaddisp.show_layer(self.layer)
        
# ---------------------------------------
import board
import busio
import usb_hid
import configure
import displayio
import adafruit_displayio_ssd1306

displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA, frequency=int(1e6))
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
macropaddisp = MONO_128x32(configure.configure, display)

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

macropad = MacroPad(
    macrokeypad=macrokeypad,
    macropaddisp=macropaddisp,
    configure=configure,
    hid=usb_hid,
)

# while True:
#     if event := macrokeypad.events.get():
#         print(event)
        
while True:
    macropad()
