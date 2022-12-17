# cpy native
import board
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
        
class MacroPad:
    def __init__(
        self,
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
    ):
        # hardware
        self.encoder=rotaryio.IncrementalEncoder(*encoder_pins)
        self.keys = keypad.Keys(
            key_pins, 
            pull=True,
            value_when_pressed=False
        )
        # queue
        self._events = EventQueue()
        
    @property
    def events(self):
        position = self.encoder.position
        if position != 0:
            key_number = 7 if position > 0 else 8
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
    

pad = MacroPad()
while True:
    if event := pad.events.get():
        print(event)