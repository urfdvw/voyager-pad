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
        configure,
        hid,
    ):
        self.macrokeypad = macrokeypad
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
            
    def release_code(self, code):
        if code in Keycode.__dict__:
            self.keyboard.release(Keycode.__dict__[code])
        elif code in ConsumerControlCode.__dict__:
            self.consumer_control.release()
        elif code in Mouse.__dict__:
            self.mouse.release(Mouse.__dict__[code])
            
    def press_sec(self, sec):
        if len(sec[0]) == 0:
            return
        if sec[0][0] == "'":
            return
        else:
            for code in sec:
                self.press_code(code)
            
    def release_sec(self, sec):
        if len(sec[0]) == 0:
            return
        if sec[0][0] == "'":
            self.keyboard_layout.write(sec[0][1:-1])
        else:
            for code in sec:
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
            if self.n_layer_key_press == 0:
                self.layer = -1
        # get sequence
        else:
            seq = self.configure.sequence[self.layer][event.key_number]
            
            # print(seq)
            if event.pressed:
                for i in range(len(seq)):
                    self.press_sec(seq[i])
                    if i != len(seq) - 1:
                        self.release_sec(seq[i])
            else:
                self.release_sec(seq[-1])
        
# ---------------------------------------
import board
import usb_hid
import configure

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
        
while True:
    macropad()
