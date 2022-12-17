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


from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

Keycode_names = {Keycode.__dict__[k]: k for k in Keycode.__dict__ if k[0].isupper()}
ConsumerControlCode_names = {ConsumerControlCode.__dict__[k]: k for k in ConsumerControlCode.__dict__ if k[0].isupper()}

from configure import configure
       
class MacroPad:
    def __init__(
        self,
        macrokeypad,
        configure,
        hid,
    ):
        self.macrokeypad = macrokeypad
        self.configure = configure
        
        self.layer = 0
        self.n_layer_key_press = 0
        self.n_key_press = 0
        
        
        self.kbd = Keyboard(hid.devices)
        self.consumer_control = ConsumerControl(hid.devices)
        
    def __call__(self):
        pass

import board
import usb_hid

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
    configure=configure,
    hid=usb_hid,
)

# while True:
#     if event := macrokeypad.events.get():
#         print(event)
