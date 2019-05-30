import board
import busio
import adafruit_pca9685
from gpiozero import LED

i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)

pca.frequency = 50

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

# PWM Controller

# 0 - Intake
# 1 - Back Climb
# 2 - Double climb release
# 3 - Left FWD
# 4 - Left REV
# 5 - Right FWD
# 6 - Right REV

# Main
# 4 - Elevator ENable
# 17 - Elevator down
# 27 - Left Enable
# 22 - Right Enable

INTAKE = 0
BACK_CLIMB = 1
DOUBLE_CLIMB = 2

LEFT_FWD = 3
LEFT_REV = 4

RIGHT_FWD = 5
RIGHT_REV = 6

ELEVATOR_ENABLE = 4
ELEVATOR_DOWN = 17

LEFT_ENABLE = 27
RIGHT_ENABLE = 22

elevator_enable_io = LED(ELEVATOR_ENABLE)
elevator_enable_io.on()

elevator_down_io = LED(ELEVATOR_DOWN)
elevator_down_io.on()

left_enable = LED(LEFT_ENABLE)
right_enable = LED(RIGHT_ENABLE)

# Big boi servo
kit.servo[2].set_pulse_width_range(1500, 2500)

def continuous_ccw(channel):
    pca.channels[channel].duty_cycle = 5000

def continuous_cw(channel):
    pca.channels[channel].duty_cycle = 50

def continuous_stop(channel):
    pca.channels[channel].duty_cycle = 0

def go_to_angle(channel, angle):
    kit.servo[channel].angle = angle

def elevator_up():
    elevator_down_io.on()
    elevator_enable_io.off()

def elevator_down():
    elevator_down_io.off()
    elevator_enable_io.off()

def elevator_stop():
    elevator_enable_io.on()

def left_control(speed):
    if speed > 0:
        pca.channels[LEFT_FWD].duty_cycle = int((speed / 255) * 65535)

    else:
        pca.channels[LEFT_FWD].duty_cycle = 0

    if speed < 0:
        pca.channels[LEFT_REV].duty_cycle = int((speed / 255) * 65535)
    else:
        pca.channels[LEFT_REV].duty_cycle = 0

    if speed != 0:
        left_enable.on()
    else:
        left_enable.off()
        
def right_control(speed):
    if speed > 0:
        pca.channels[RIGHT_FWD].duty_cycle = int((speed / 255) * 65535)

    else:
        pca.channels[RIGHT_FWD].duty_cycle = 0

    if speed < 0:
        pca.channels[RIGHT_REV].duty_cycle = int((speed / 255) * 65535)
    else:
        pca.channels[RIGHT_REV].duty_cycle = 0

    if speed != 0:
        right_enable.on()
    else:
        right_enable.off()
