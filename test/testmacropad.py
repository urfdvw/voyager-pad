import rotaryio
import board

encoder = rotaryio.IncrementalEncoder(board.D8, board.D7)
last_position = None
    
import keypad
keys = keypad.Keys(
    (
        board.D10, # lower row
        board.D6,
        board.D3, # upper row
        board.D2,
        board.D1,
        board.D0,
        board.D9, # nob
    ), 
    pull=True,
    value_when_pressed=False
)

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

events = EventQueue()

i2c = board.I2C()
import displayio
from terminalio import FONT
import adafruit_ssd1306
from adafruit_display_text import label

display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Make the display context
draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)

while True:
    position = encoder.position
    if position != 0:
        key_number = 7 if position > 0 else 8
        position = abs(position)
        for i in range(position):
            events.append(
                keypad.Event(
                    key_number=key_number,
                    pressed=True,
                )
            )
            events.append(
                keypad.Event(
                    key_number=key_number,
                    pressed=False,
                )
            )
        encoder.position = 0
            
    while True:
        event = keys.events.get()
        if event is None:
            break
        events.append(event)
        
    event = events.get()
    if event:
        print(event)
        text_area.text = str(event.key_number)