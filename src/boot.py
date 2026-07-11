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

# Enable a USB video (UVC) framebuffer so the OLED content can be mirrored
# to the host computer as a webcam feed. Must be sized and enabled here in
# boot.py -- it cannot be changed later at runtime. Matches the physical
# OLED's 128x32 resolution so the same content can be mirrored 1:1.
import usb_video
usb_video.enable_framebuffer(128, 32)
