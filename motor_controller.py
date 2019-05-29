import board
import busio
import adafruit_pca9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)

pca.frequency = 50

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

# 0 - Intake
# 1 - Back Climb
# 2 - Double climb release
# 3 - Left FWD
# 4 - Left REV
# 5 - Right FWD
# 6 - Right REV

LEFT_FWD = 3
LEFT_REV = 4

RIGHT_FWD = 5
RIGHT_REV = 6

# Big boi servo
kit.servo[2].set_pulse_width_range(1500, 2500)

def continuous_ccw(channel):
    pca.channels[channel].duty_cycle = 10000

def continuous_cw(channel):
    pca.channels[channel].duty_cycle = 50

def continuous_stop(channel):
    pca.channels[channel].duty_cycle = 0

def go_to_angle(channel, angle):
    kit.servo[channel].angle = angle

def left_control(speed):
    if speed > 0:
        pca.channels[LEFT_FWD].duty_cycle = int((speed / 255) * 65535)

    else:
        pca.channels[LEFT_FWD].duty_cycle = 0

    if speed < 0:
        pca.channels[LEFT_REV].duty_cycle = int((speed / 255) * 65535)
    else:
        pca.channels[LEFT_REV].duty_cycle = 0
        
def right_control(speed):
    if speed > 0:
        pca.channels[RIGHT_FWD].duty_cycle = int((speed / 255) * 65535)

    else:
        pca.channels[RIGHT_FWD].duty_cycle = 0

    if speed < 0:
        pca.channels[RIGHT_REV].duty_cycle = int((speed / 255) * 65535)
    else:
        pca.channels[RIGHT_REV].duty_cycle = 0