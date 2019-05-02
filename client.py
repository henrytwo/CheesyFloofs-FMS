import socket
import pickle
import multiprocessing
from pygame import *

def send_command(command_queue, sock, address):

    while True:
        data_out = command_queue.get()
        print('sending')
        sock.sendto(data_out, address)


def get_data(recv_queue, sock):

    while True:
        msg = sock.recvfrom(1024)
        recv_queue.put(pickle.loads(msg))

if __name__ == '__main__':
    screen = display.set_mode((500, 500))

    host = '127.0.0.1' #input('Host> ')
    port = 25565 #int(input('Port> '))

    address = (host, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    running = True
    pos = [0, 0]

    command_queue = multiprocessing.Queue()
    recv_queue = multiprocessing.Queue()

    send_process = multiprocessing.Process(target=send_command, args=(command_queue, sock, address))
    recv_process = multiprocessing.Process(target=get_data, args=(recv_queue, sock))

    send_process.start()
    recv_process.start()

    keys = {}

    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
                send_process.terminate()
                recv_process.terminate()

        screen.fill((255, 255, 255))
        draw.circle(screen, (255, 0, 0), pos, 2)

        # W - 119
        # A - 97
        # S - 115
        # D - 100
        # SPC - 32

        keys['R'] = key.get_pressed()[114]
        keys['F'] = key.get_pressed()[102]
        keys['W'] = key.get_pressed()[119]
        keys['A'] = key.get_pressed()[97]
        keys['S'] = key.get_pressed()[115]
        keys['D'] = key.get_pressed()[100]
        keys['SPC'] = key.get_pressed()[32]

        commands = pickle.dumps(keys)

        for k in keys:
            if keys[k] == 1:
                break

        command_queue.put(commands)

        try:
            in_data = recv_queue.get_nowait()

            if in_data:
                pos = in_data
        except:
            pass

        print(pos, keys)

        display.flip()