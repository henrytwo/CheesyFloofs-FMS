import socket
import pickle
import threading
import multiprocessing
import time
import led_controller

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


def processor(send, recv):

    enabled = False

    while True:

        msg, addr = recv.get()

        # do stuff

        if msg['SPC']:
            #led.on()

            enabled = not enabled

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
    command_processor = multiprocessing.Process(target=processor, args=(send_queue, recv_queue))

    send_procress.start()
    recv_procress.start()
    command_processor.start()

    print('Server running on', addr)
