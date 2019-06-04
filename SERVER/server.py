import socket
import pickle
import threading
import multiprocessing
import time
import led_controller
import motor_controller
import traceback
import uuid

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


RECORD_INTERVAL = 0.1
PWM_OE = 10

# Checks if code is running on pi
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

# LED processing process
def led_processor(q):
    current_command = 'fade'

    while True:

        try:
            current_command = q.get_nowait()
        except:
            pass

        led_controller.cycle(current_command)

# Checks if a driverstation command is active
def commcheck(base, index):
    return index in base and base[index]

# Safety feature to ensure DS is in constant communication
def watchdog(watchqueue, recv):
    last_time = -1

    while True:

        try:
            last_time = watchqueue.get_nowait()
        except:
            pass

        # If Latency > 1s, kill robot
        if time.time() - last_time > 1 and last_time != -1:
            recv.put(('WATCHDOG', -1))

        time.sleep(0.5)

def update_robot(msg):
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

        # Drive train keyboard
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

            new_elevator_direction = 1
        elif commcheck(msg, 'J'):
            motor_controller.elevator_down()

            new_elevator_direction = -1
        else:
            motor_controller.elevator_stop()

            new_elevator_direction = 0

        # Intake
        if commcheck(msg, 'K'):  # succ
            motor_controller.continuous_cw(motor_controller.INTAKE)
            print('succc')
        elif commcheck(msg, 'I'):  # unsucc
            motor_controller.continuous_ccw(motor_controller.INTAKE)
            print('unsucc')
        else:
            motor_controller.continuous_stop(motor_controller.INTAKE)

        # Back Climb
        if commcheck(msg, 'O'):  # leg up
            motor_controller.continuous_cw(motor_controller.BACK_CLIMB)
        elif commcheck(msg, 'L'):  # leg down
            motor_controller.continuous_ccw(motor_controller.BACK_CLIMB)
        else:
            motor_controller.continuous_stop(motor_controller.BACK_CLIMB)

        # Double climb bar
        if commcheck(msg, 'PD'):  # Deploy
            motor_controller.go_to_angle(motor_controller.DOUBLE_CLIMB, 180)
        elif commcheck(msg, 'PU'):  # Reset
            motor_controller.go_to_angle(motor_controller.DOUBLE_CLIMB, 0)

        # Makes led strips chase based on elevator direction
        if elevator_direction != new_elevator_direction:
            elevator_direction = new_elevator_direction

            if elevator_direction == 1:
                print('led up')
                led_queue.put('chase_up')
            elif elevator_direction == -1:
                print('led down')
                led_queue.put('chase_down')
            else:
                print('reset position')
                led_queue.put('rainbow')


    except:
        print('Error occured')
        led_queue.put('error')

        traceback.print_exc()

def autonomous(auto_instruction_queue, auto_interrupt_queue):
    while True:
        instruction = auto_instruction_queue.get()

        for i in instruction:
            update_robot(i)

            time.sleep(RECORD_INTERVAL)

            try:
                interrupt_packet = auto_interrupt_queue.get_nowait()

                if interrupt_packet:
                    break
            except:
                pass

# Primary command processor
def processor(send, recv, led_queue, watchdog_queue, auto_instruction_queue, auto_interrupt_queue):

    enabled = False

    pwm_oe = LED(PWM_OE)
    pwm_oe.on()

    last_comm = -1
    last_ds_time = -1

    elevator_direction = 0
    new_elevator_direction = 0

    last_update = -1

    recording = False
    recording_stack = []
    previous_frame = -1


    while True:

        try:
            # Get latest command
            msg, addr = recv.get()

            # Check if command is issued by watchdog
            if msg != 'WATCHDOG':

                # Ensure command was issued within the last second
                if last_ds_time == -1 or abs((time.time() - last_comm + last_ds_time) - msg['ds_time']) < 1:

                    last_comm = time.time()
                    last_ds_time = msg['ds_time']

                else: # Too much lag, command ignored
                    msg = {}
                    print('Command tossed due to lag', abs((time.time() - last_comm + last_ds_time) - msg['ds_time']))

                # If latency is with 0.5s, tell watchdog everything is good
                if time.time() - last_update > 0.5:
                    last_update = time.time()
                    watchdog_queue.put(last_comm)

            elif enabled: # Stop command issued by watchdog
                enabled = False
                print('WATCHDOG STOPPED')

                led_queue.put('watchdog')


        except:
            msg = {}

        # Enable and disable robot
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
            pwm_oe.off() # Enable motor power

            if msg and msg['mode'] == 'teleop':

                # Begin recording
                if commcheck(msg, 'R'):
                    recording = True

                elif commcheck(msg, 'F'):
                    recording = False

                    filename = 'test.auto' #str(uuid.uuid4()) + '.auto'

                    with open(filename, 'wb') as file:
                        pickle.dump(recording_stack, file)

                    print('Saved as ' + filename)



                if recording:

                    if previous_frame == -1 or time.time() > previous_frame + RECORD_INTERVAL:
                        recording_stack.append(msg)
                        previous_frame = time.time()

                update_robot(msg)

            elif msg and msg['mode'] == 'auto':

                with open('test.auto', 'rb') as file:
                    file = pickle.load(file)

                    auto_instruction_queue.put(file)



        else:
            # Kills elevator and servo control
            pwm_oe.on()
            motor_controller.elevator_enable_io.on()

            auto_interrupt_queue.put('STOP')

            # Flush queue to get rid of residual instructions that might otherwise do bad things
            try:
                while True:
                    auto_instruction_queue.get_nowait()
            except:
                pass

        #print(enabled, msg)

        # Reminds drive station that robot is indeed alive
        if msg:
            send.put(({'heartbeat':'I am alive!', 'elevator': 0, 'recording': recording}, addr))

#L9u3EhzpU


if __name__ == '__main__':

    if ON_PI:
        addr = ('192.168.0.100', 6969)
    else:
        addr = ('localhost', 6969)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(addr)

    # Multiprocessing queues
    send_queue = multiprocessing.Queue()
    recv_queue = multiprocessing.Queue()
    led_queue = multiprocessing.Queue()
    watchdog_queue = multiprocessing.Queue()

    auto_instruction_queue = multiprocessing.Queue()
    auto_interrupt_queue = multiprocessing.Queue()

    # Setup processes
    send_procress = multiprocessing.Process(target=send_messages, args=(send_queue, sock))
    recv_procress = multiprocessing.Process(target=recv_messages, args=(recv_queue, sock))
    command_processor = multiprocessing.Process(target=processor, args=(send_queue, recv_queue, led_queue, watchdog_queue, auto_instruction_queue, auto_interrupt_queue))
    watchdog_processor = multiprocessing.Process(target=watchdog, args=(watchdog_queue, recv_queue))
    auto_processor = multiprocessing.Process(target=autonomous, args=(auto_instruction_queue, auto_interrupt_queue))

    led_process = multiprocessing.Process(target=led_processor, args=(led_queue,))

    # Start processes
    send_procress.start()
    recv_procress.start()
    command_processor.start()
    led_process.start()
    watchdog_processor.start()
    auto_processor.start()

    print('Server running on', addr)
