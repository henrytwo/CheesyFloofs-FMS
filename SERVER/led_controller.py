import time
import board
import neopixel
import math

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 10

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels * 2, brightness=1, auto_write=False,
                           pixel_order=ORDER)

rainbow_count = 0

# Makes both sides the same
def dual(index, value):

    pixels[index] = value
    pixels[num_pixels * 2 - 1 - index] = value


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)


def rainbow_cycle(wait=0.00001):

    global rainbow_count

    for i in range(num_pixels):
        pixel_index = (i * 256 // num_pixels) + rainbow_count
        #pixels[i] = wheel(pixel_index & 255)
        dual(i, wheel(pixel_index & 255))
    pixels.show()

    rainbow_count += 1
    rainbow_count %= 255
    #time.sleep(wait)

def chase(color, direction):

    pixels.fill((0, 0, 0))


    if direction > 0:
        index = int(time.time() * 20) % num_pixels

    else:
        index = num_pixels - int(time.time() * 20) % num_pixels

    for i in range(5):

        if -1 < (i + index) % num_pixels < num_pixels:

            dual((i + index) % num_pixels, color)

def chase_up():
    chase((0, 0, 255), 1)

def chase_down():
    chase((0, 0, 255), -1)

def fade():
    pixels.fill((0, 0, int(128 * math.sin(time.time() * 3) + 128)))

def watchdog():
    pixels.fill((255 if int(time.time() * 2) % 2 == 0 else 0, 0, 0))

def error():
    pixels.fill((255, 255, 0) if int(time.time() * 2) % 2 == 0 else (0, 0, 0))

command_list = {'fade': fade,
                'watchdog': watchdog,
                'rainbow': rainbow_cycle,
                'chase_up': chase_up,
                'chase_down': chase_down,
                'error': error}

def cycle(command):

    #print(command)

    command_list[command]()
    pixels.show()
