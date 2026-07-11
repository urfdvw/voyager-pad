# enable gc
import gc
gc.enable()
# turn off auto reload to prevent unexpected break
import supervisor
supervisor.runtime.autoreload = False

# Note: GamePad is no longer available as an Adafruit HID device, so only
# keyboard, mouse and consumer control are enabled here.
import usb_hid

usb_hid.enable(
    (
        usb_hid.Device.KEYBOARD,
        usb_hid.Device.MOUSE,
        usb_hid.Device.CONSUMER_CONTROL,
    )
)
