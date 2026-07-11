# python native
from time import monotonic, sleep
# hardware libs
import rotaryio
import keypad
# display libs
import displayio
from terminalio import FONT
from adafruit_display_text.label import Label
from adafruit_display_text import wrap_text_to_lines
# hid libs
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.mouse import Mouse

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



# Shared layout constants + text-building helper, used by BOTH display
# renderers below (the OLED's MONO_128x32 and the USB video mirror
# USBVideoMirror) so the two stay visually in sync and the per-layer
# text-wrapping logic isn't duplicated between them.
LAYER_TEXT_Y = 5
MACRO_TEXT_Y = 15
MACRO_TEXT_SCALE = 2


def build_layer_text(configure_data, width_px=128, char_width=6):
    """Build the per-layer wrapped summary text (e.g. '2:Mute 3:Prev ...')
    shown on both displays, from a configure module's `.configure` dict."""
    return {
        layer: '\n'.join(wrap_text_to_lines(
            ' '.join([
                str(key_number) + ':' + configure_data[layer][key_number][0]
                for key_number in sorted(configure_data[layer].keys())
                if configure_data[layer][key_number][0]
            ])
        , width_px // char_width)
        )
        for layer in configure_data
    }


class MacroPadDisplay:
    def __init__(self, display):
        self.display = display
        self.splash = displayio.Group()
        self.display.root_group = self.splash

        self.layer_group = displayio.Group()
        self.splash.append(self.layer_group)
        self.layer_group.hidden = False
        self.layer_lable = Label(
            FONT,
            text='',
        )
        self.layer_group.append(self.layer_lable)

        self.macro_group = displayio.Group()
        self.splash.append(self.macro_group)
        self.macro_group.hidden = True
        self.macro_lable = Label(
            FONT,
            text='',
            scale=MACRO_TEXT_SCALE,
        )
        self.macro_group.append(self.macro_lable)

        self.layer = -1
        self.state = 0

    def show_layer_text(self, text):
        if (self.layer_lable.text == text
        and self.state == 0):
            return
        self.state = 0
        self.layer_lable.text = text
        self.layer_group.hidden = False
        self.macro_group.hidden = True

    def show_macro_text(self, text):
        if (self.macro_lable.text == text
        and self.state == 1):
            return
        self.state = 1
        self.macro_lable.text = text
        self.layer_group.hidden = True
        self.macro_group.hidden = False


class MONO_128x32(MacroPadDisplay):
    def __init__(self, configure, display):
        super().__init__(display)
        self.configure = configure.configure
        self.layer_text = build_layer_text(self.configure)
        # print(self.layer_text)

        self.layer_lable.color=0xFFFFFF
        self.layer_lable.background_color=0x000000
        self.layer_lable.x=0
        self.layer_lable.y=LAYER_TEXT_Y
        self.layer_lable.line_spacing=0.8

        self.macro_lable.color=0xFFFFFF
        self.macro_lable.background_color=0x000000
        self.macro_lable.x=0
        self.macro_lable.y=MACRO_TEXT_Y
        
        self.show_layer(-1)

    def show_layer(self, layer):
        self.layer = layer
        text = self.layer_text[layer]
        self.show_layer_text(text)

    def show_macro(self, key_number):
        text = self.configure[self.layer][key_number][0]
        self.show_macro_text(text)


class USBVideoMirror:
    """Mirrors the same layer/macro text shown on the OLED to a USB video
    (UVC) framebuffer (usb_video.USBFramebuffer, enabled in boot.py).

    This board's CircuitPython build only supports a single displayio
    Display at a time, so the USB video output cannot be wrapped in its
    own framebufferio.FramebufferDisplay while the OLED is active. Instead
    this renders the built-in terminalio font directly onto a private
    displayio.Bitmap "canvas" and pushes the result as raw RGB565 pixels
    into the framebuffer's buffer protocol, bypassing displayio.Display
    entirely."""

    def __init__(self, configure, framebuffer):
        self.configure = configure.configure
        self.layer_text = build_layer_text(self.configure)
        self.layer = -1
        self.state = 0
        self._layer_cache = None
        self._macro_cache = None

        self.fb = framebuffer
        self.width = framebuffer.width
        self.height = framebuffer.height
        self.canvas = displayio.Bitmap(self.width, self.height, 2)
        self.mv = memoryview(framebuffer)

    def _clear(self):
        for i in range(self.width * self.height):
            self.canvas[i] = 0

    def _draw_text(self, text, x0, y0, scale=1):
        # Label anchors 'y' at the vertical center of the glyph cell
        # (bounding_box top is -6 in font-native units); match that here
        # so the mirrored text lines up with the OLED's Label-based text.
        x, y = x0, y0 - 6 * scale
        for ch in text:
            if ch == '\n':
                y += int(12 * scale * 0.8)
                x = x0
                continue
            gl = FONT.get_glyph(ord(ch))
            if gl is None:
                x += 6 * scale
                continue
            gx0 = gl.tile_index * gl.width
            for row in range(gl.height):
                for col in range(gl.width):
                    if gl.bitmap[gx0 + col, row]:
                        for sy in range(scale):
                            for sx in range(scale):
                                px = x + col * scale + sx
                                py = y + row * scale + sy
                                if 0 <= px < self.width and 0 <= py < self.height:
                                    self.canvas[px, py] = 1
            x += gl.shift_x * scale

    def _push(self):
        for i in range(self.width * self.height):
            self.mv[i] = 0xFFFF if self.canvas[i] else 0x0000
        self.fb.refresh()

    def show_layer_text(self, text):
        if text == self._layer_cache and self.state == 0:
            return
        self.state = 0
        self._layer_cache = text
        self._clear()
        self._draw_text(text, 0, LAYER_TEXT_Y, scale=1)
        self._push()

    def show_macro_text(self, text):
        if text == self._macro_cache and self.state == 1:
            return
        self.state = 1
        self._macro_cache = text
        self._clear()
        self._draw_text(text, 0, MACRO_TEXT_Y, scale=MACRO_TEXT_SCALE)
        self._push()

    def show_layer(self, layer):
        self.layer = layer
        self.show_layer_text(self.layer_text[layer])

    def show_macro(self, key_number):
        self.show_macro_text(self.configure[self.layer][key_number][0])


class MultiDisplay:
    """Forwards display calls to multiple display-wrapper objects (e.g. an
    adafruit_displayio_ssd1306 OLED and a usb_video framebuffer) so the same
    content can be shown/mirrored on all of them at once."""
    def __init__(self, displays):
        self.displays = displays

    def show_layer_text(self, text):
        for d in self.displays:
            d.show_layer_text(text)

    def show_macro_text(self, text):
        for d in self.displays:
            d.show_macro_text(text)

    def show_layer(self, layer):
        for d in self.displays:
            d.show_layer(layer)

    def show_macro(self, key_number):
        for d in self.displays:
            d.show_macro(key_number)


class MacroPad:
    def __init__(
        self,
        macrokeypad,
        configure,
        hid,
        macropaddisp=None,
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

        self.cur_macro = ''

        if self.macropaddisp:
            self.start_time = monotonic()
            self.CD = 1
            self.displaying_macro = False

    def press_code(self, code):
        if code in Keycode.__dict__:
            self.keyboard.press(Keycode.__dict__[code])
        elif code in ConsumerControlCode.__dict__:
            self.consumer_control.press(ConsumerControlCode.__dict__[code])
        elif code in Mouse.__dict__:
            self.mouse.press(Mouse.__dict__[code])
        elif code.startswith('MOUSE_MOVE'):
            x, y, w = [int(axis) for axis in code.split('_')[-3:]]
            self.mouse.move(x=x,y=y,wheel=w)
        elif code.startswith('WAIT'):
            ms = int(code.split('_')[-1])
            sleep(ms / 1000)
        else:
            raise ValueError(
                'Bad Key Code:' + code
            )

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
            for code in reversed(hotkey):
                self.release_code(code)

    def __call__(self):
        # reset layer screen
        if self.macropaddisp and self.displaying_macro:
            if (monotonic() - self.start_time > self.CD
            and self.n_key_press == 0):
                self.macropaddisp.show_layer(self.layer)
                self.displaying_macro = False
        # get event
        event = self.macrokeypad.events.get()
        if event is None:
            return
        # count press
        if event.key_number in self.configure.configure:
            self.n_layer_key_press += 1 if event.pressed else -1
        else:
            self.n_key_press += 1 if event.pressed else -1
        # get layer
        if event.key_number in self.configure.configure:
            if event.pressed:
                # release all keys
                self.keyboard.release_all()
                self.mouse.release_all()
                self.consumer_control.release()
                # change layer
                self.layer = event.key_number
                if self.macropaddisp:
                    self.macropaddisp.show_layer(self.layer)
            if self.n_layer_key_press == 0:
                self.layer = -1
                if self.macropaddisp:
                    self.macropaddisp.show_layer(self.layer)
        # get macro
        else:
            self.cur_macro = self.configure.macro[self.layer][event.key_number]
            
            # print(self.cur_macro)
            if event.pressed:
                for i in range(len(self.cur_macro)):
                    self.press_hotkey(self.cur_macro[i])
                    if i != len(self.cur_macro) - 1:
                        self.release_hotkey(self.cur_macro[i])
                if self.macropaddisp:
                    self.macropaddisp.show_macro(event.key_number)
                    self.displaying_macro = True
                    self.start_time = monotonic()
            else:
                self.release_hotkey(self.cur_macro[-1])
