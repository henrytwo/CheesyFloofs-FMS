import socket
import pickle
import threading
import multiprocessing
import time
import led_controller
import motor_controller
import traceback

# Main Pi

# 2 - PWM
# 3 - PWM
# 4 - Elevator ENable
# 17 - Elevator down
# 27 - Left FWD Enable
# 22 - Left BW Enable
# 10 - PWM OE
# 9 - Right FWD Enable
# 11 - Right BW Enable
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

PWM_OE = 10

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
    current_command = 'fade'

    while True:

        try:
            current_command = q.get_nowait()
        except:
            pass

        led_controller.cycle(current_command)

def commcheck(base, index):
    return index in base and base[index]

def watchdog(watchqueue, recv):
    last_time = -1

    while True:

        try:
            last_time = watchqueue.get_nowait()
        except:
            pass

        if time.time() - last_time > 0.5:
            recv.put(('WATCHDOG', -1))


        pass

def processor(send, recv, led_queue, watchdog_queue):

    enabled = False

    pwm_oe = LED(PWM_OE)
    pwm_oe.on()

    last_comm = -1

    while True:

        try:
            msg, addr = recv.get()

            if msg != 'WATCHDOG':

                last_comm = time.time()
                watchdog_queue.put(last_comm)

            else:
                last_comm = -1

        except:
            msg = {}

        if time.time() - last_comm > 0.5 and enabled:
            enabled = False
            print('WATCHDOG STOPPED')


            led_queue.put('watchdog')

        # do stuff

        if commcheck(msg, 'enabled') and not enabled:

            print('Robot enabled!')

            led_queue.put('rainbow')

            enabled = True

        # only queue up instruction once to avoid flooding
        elif not commcheck(msg, 'enabled') and enabled:
            led_queue.put('fade')

            enabled = False

            print('Robot disabled by DS')

        if enabled:
            pwm_oe.off()

            # Controls needed
            # WASD - Drive, duh
            # UJ - Elevator
            # IK - Intake
            # OL - Back Climb
            # PU PD - Double Climb release

            # Primary Drive Train
            left_power = 0
            right_power = 0

            turning = False

            try:


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

                if commcheck(msg, 'R'):
                    motor_controller.continuous_ccw(motor_controller.INTAKE)
                elif commcheck(msg, 'F'):
                    motor_controller.continuous_cw(motor_controller.INTAKE)
                else:
                    motor_controller.continuous_stop(motor_controller.INTAKE)

                if turning:
                    if left_power > 255:
                        left_power /= 2
                    if right_power > 255:
                        right_power /= 2

                motor_controller.left_control(left_power)
                motor_controller.right_control(right_power)

                # Elevator
                if commcheck(msg, 'U'):
                    motor_controller.elevator_up()
                elif commcheck(msg, 'J'):
                    motor_controller.elevator_down()
                else:
                    motor_controller.elevator_stop()

                # Intake
                if commcheck(msg, 'K'): #succ
                    motor_controller.continuous_cw(motor_controller.INTAKE)
                    print('succc')
                elif commcheck(msg, 'I'): #unsucc
                    motor_controller.continuous_ccw(motor_controller.INTAKE)
                    print('unsucc')
                else:
                    motor_controller.continuous_stop(motor_controller.INTAKE)

                # Back Climb
                if commcheck(msg, 'O'): #leg up
                    motor_controller.continuous_cw(motor_controller.BACK_CLIMB)
                elif commcheck(msg, 'L'): #leg down
                    motor_controller.continuous_ccw(motor_controller.BACK_CLIMB)
                else:
                    motor_controller.continuous_stop(motor_controller.BACK_CLIMB)

            except:
                print('Error occured')
                led_queue.put('error')

                traceback.print_exc()


        else:
            pwm_oe.off()

        #print(enabled, msg)

        if msg:
            send.put(({'heartbeat':'I am alive!', 'elevator': 0}, addr))

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
    watchdog_queue = multiprocessing.Queue()

    send_procress = multiprocessing.Process(target=send_messages, args=(send_queue, sock))
    recv_procress = multiprocessing.Process(target=recv_messages, args=(recv_queue, sock))
    command_processor = multiprocessing.Process(target=processor, args=(send_queue, recv_queue, led_queue, watchdog_queue))
    watchdog_processor = multiprocessing.Process(target=watchdog, args=(watchdog_queue, recv_queue))

    led_process = multiprocessing.Process(target=led_processor, args=(led_queue,))

    send_procress.start()
    recv_procress.start()
    command_processor.start()
    led_process.start()
    watchdog_processor.start()

    print('Server running on', addr)
