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

LEFT = 3
RIGHT = 4


ELEVATOR_ENABLE = 4
ELEVATOR_DOWN = 17

LEFT_FWD_ENABLE = 19
LEFT_REV_ENABLE = 13
RIGHT_FWD_ENABLE = 9
RIGHT_REV_ENABLE = 11

left_fwd_io = LED(LEFT_FWD_ENABLE)
left_rev_io = LED(LEFT_REV_ENABLE)
right_fwd_io = LED(RIGHT_FWD_ENABLE)
right_rev_io = LED(RIGHT_REV_ENABLE)

elevator_enable_io = LED(ELEVATOR_ENABLE)
elevator_enable_io.on()

elevator_down_io = LED(ELEVATOR_DOWN)
elevator_down_io.on()

# Big boi servo
kit.servo[2].set_pulse_width_range(1500, 2500)

# Run servo ccw
def continuous_ccw(channel):
    pca.channels[channel].duty_cycle = 2553

# Run servo cw
def continuous_cw(channel):
    pca.channels[channel].duty_cycle = 50

# Stop servo
def continuous_stop(channel):
    pca.channels[channel].duty_cycle = 0

# non continuous servo position
def go_to_angle(channel, angle):
    kit.servo[channel].angle = angle

# Elevator Up
def elevator_up():
    elevator_down_io.off()
    elevator_enable_io.off()

    print('UP')

# Elevator down
def elevator_down():
    elevator_down_io.on()
    elevator_enable_io.off()

    print('DOWN')

# Stop elevator
def elevator_stop():
    elevator_enable_io.on()

# Control left drivetrain
def left_control(speed):
    #pca.channels[LEFT].duty_cycle = int((abs(speed) / 255) * 65535)

    #print('LEFT', speed, int((abs(speed) / 255) * 65535))

    # Toggles left and right enable
    if speed > 0:
        left_fwd_io.on()
        left_rev_io.off()


    elif speed < 0:
        left_fwd_io.off()
        left_rev_io.on()

    else:
        left_fwd_io.off()
        left_rev_io.off()

        #pca.channels[LEFT].duty_cycle = 0

# Control right drive train
def right_control(speed):
    #pca.channels[RIGHT].duty_cycle = int((abs(speed) / 255) * 65535)


    #print('RIGHT', speed, int((abs(speed) / 255) * 65535))

    if speed > 0:
        right_fwd_io.on()
        right_rev_io.off()


    elif speed < 0:
        right_fwd_io.off()
        right_rev_io.on()

    else:
        right_fwd_io.off()
        right_rev_io.off()

        #pca.channels[RIGHT].duty_cycle = 0