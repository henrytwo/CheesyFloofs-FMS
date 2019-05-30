import socket
import pickle
import threading
import multiprocessing
import time
import led_controller
import motor_controller

# Main Pi

# 2 - PWM
# 3 - PWM
# 4 - Elevator ENable
# 17 - Elevator down
# 27 - Left Enable
# 22 - Right Enable
# 10
# 9
# 11
# 5
# 6
# 13
# 19
# 26

# 14
# 15
# 18 - LED
# 23
# 24
# 25
# 8
# 7
# 12
# 16
# 20
# 21

try:
    from gpiozero import LED

    ON_PI = True

except:
    from fakepi import LED

    ON_PI = False

def recv_messages(recv_queue, sock):
    while True:
        try:
            msg = sock.recvfrom(1024)
            recv_queue.put([pickle.loads(msg[0]), msg[1]])
        except:
            pass

def send_messages(send_queue, sock):
    while True:
        try:
            msg = send_queue.get()
            sock.sendto(pickle.dumps(msg[0]), msg[1])
        except:
            pass

def led_processor(q):
    while True:
        current_command = 'fade'


        try:
            current_command = q.get_nowait()
        except:
            pass

        led_controller.cycle(current_command)

def commcheck(base, index):
    return index in base and base[index]

def processor(send, recv, led_queue):

    enabled = False

    last_comm = -1

    disabled_led = False

    while True:

        try:
            msg, addr = recv.get()

            last_comm = time.time()

        except:
            msg = {}

        if time.time() - last_comm > 2 and enabled:
            enabled = False
            print('WATCHDOG STOPPED')


            led_queue.put('watchdog')

        # do stuff

        if commcheck(msg, 'enabled'):

            led_queue.put('rainbow')

            #led.on()

            enabled = not enabled

            disabled_led = False

        # only queue up instruction once to avoid flooding
        elif not disabled_led:
            disabled_led = True
            led_queue.put('fade')

        left_power = 0
        right_power = 0

        turning = False

        if commcheck(msg, 'W'):
            left_power += 255
            right_power += 255

        if commcheck(msg, 'S'):
            left_power -= 255
            right_power -= 255

        if commcheck(msg, 'A'):
            left_power -= 255
            right_power += 255

            turning = True

        if commcheck(msg, 'D'):
            left_power += 255
            right_power -= 255

            turning = True

        try:
            if commcheck(msg, 'R'):
                motor_controller.continuous_cw(motor_controller.INTAKE)
            elif commcheck(msg, 'F'):
                motor_controller.continuous_ccw(motor_controller.INTAKE)
            else:
                motor_controller.continuous_stop(motor_controller.INTAKE)
        except:
            pass

        if turning:
            left_power /= 2
            right_power /= 2

        #motor_controller.left_control(left_power)
        #motor_controller.right_control(right_power)

        """
        if commcheck(msg, 'R'):
            motor_controller.elevator_up()
        elif commcheck(msg, 'F'):
            motor_controller.elevator_down()
        else:
            motor_controller.elevator_stop()
        """
        print(enabled, msg)

#L9u3EhzpU


if __name__ == '__main__':

    if ON_PI:
        addr = ('192.168.0.100', 6969)
    else:
        addr = ('localhost', 6969)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(addr)

    send_queue = multiprocessing.Queue()
    recv_queue = multiprocessing.Queue()
    led_queue = multiprocessing.Queue()

    send_procress = multiprocessing.Process(target=send_messages, args=(send_queue, sock))
    recv_procress = multiprocessing.Process(target=recv_messages, args=(recv_queue, sock))
    command_processor = multiprocessing.Process(target=processor, args=(send_queue, recv_queue, led_queue))

    led_process = multiprocessing.Process(target=led_processor, args=(led_queue,))

    send_procress.start()
    recv_procress.start()
    command_processor.start()
    led_process.start()

    print('Server running on', addr)
