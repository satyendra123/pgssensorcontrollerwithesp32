#EXAMPLE-1 led_panel.py this is the class which handles the p10 display
import asyncio as aio
from machine import PWM, SoftSPI

class LEDPanel():
    def __init__(self, pa, pb, pclk, pdr, pe, plat, freq=1000, duty=10):
        # Pin
        self.pa = pa
        self.pb = pb
        self.pclk = pclk
        self.pdr = pdr
        self.pe = pe
        self.plat = plat

        # PWM
        self.freq = freq
        self.duty = duty
        self._pwm = PWM(pe, freq=self.freq, duty=self.duty)

        # SPI
        self._spi = SoftSPI(sck=self.pclk, mosi=self.pdr, miso=self.pe) # MISO is dummy

        # Cache
        self._cache = [bytearray(16) for k in range(4)]

    def _scanline(self, data):
        o = 0
        while 1:
            # Write cache
            self._spi.write(self._cache[o])

            # Disable PWM
            self._pwm.deinit()
            self.pe(0)

            # Latch
            self.plat(1)
            self.plat(0)

            # Row
            self.pa(o & 1)
            self.pb(o & 2)

            # Reenable PWM
            self._pwm.init(freq=self.freq, duty=self.duty)

            # Cache data
            for i in range(16): self._cache[o][i] = ~data[((3-i)%4)*16+o*4+(i//4)]

            o = (o+1) % 4

            await aio.sleep(0)

    # Execute
    def run(self, data, func):
        aio.run(aio.gather(self._scanline(data), func()))

    # Convenience without importing asyncio in main code
    def hold(self, t=0):
        return aio.sleep(t)

#
from framebuf import FrameBuffer, MONO_HLSB
from machine import Pin

from led_panel import LEDPanel

# Init
led = LEDPanel(
  pe = Pin(14, Pin.OUT),
  pa = Pin(13, Pin.OUT),
  pb = Pin(12, Pin.OUT),
  pclk = Pin(18, Pin.OUT),
  plat = Pin(19, Pin.OUT),
  pdr = Pin(23, Pin.OUT),
  freq = 1000,
  duty = 1
)

w = 32
h = 16

# FrameBuffer
ba = bytearray((w * h) // 8) # 1 bpp
fb = FrameBuffer(ba, w, h, MONO_HLSB)

# Main code
def main():
  x = 0
  while 1:
    fb.fill(0)
    fb.text("Hi,all!", x+w, 0, 1)
    fb.text("WOW!", 0, 9, 1)
    
    x = (x-1) % -96
    
    # Mandatory pause
    # Can be used as sleep
   await led.hold(50 / 1000) # msec

# Execute
# Must be last
led.run(ba, main)
