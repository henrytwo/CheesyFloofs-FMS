import socket
import pickle
import multiprocessing
from pygame import *
import sys
import time as t


def text(x, y, msg):
    Text = font.render(msg, True, (255, 255, 255))
    screen.blit(Text, (x, y))

def Robot(x, y, robotState):

    # top pole
    draw.rect(screen, (0, 255, 255), (x + 90, y - 170 - int(100 * robotState['elevator'] / ELEVATOR_MAX_VALUE) * 2, 8, 140))
    draw.rect(screen, (0, 255, 255), (x + 86, y - 50 - int(100 * robotState['elevator'] / ELEVATOR_MAX_VALUE) * 2, 8, 10))

    # secondary pole
    draw.rect(screen, (255, 255, 0), (x + 76, y - 175 - int(100 * robotState['elevator'] / ELEVATOR_MAX_VALUE), 8, 140))
    draw.rect(screen, (255, 255, 0), (x + 68, y - 50 - int(100 * robotState['elevator'] / ELEVATOR_MAX_VALUE), 8, 10))

    # main pole
    draw.rect(screen, (255, 0, 255), (x + 60, y - 160, 8, 150))

    # wheels
    draw.circle(screen, (50, 50, 50), (x - 70, y + 5), 20)
    draw.circle(screen, (50, 50, 50), (x + 70, y + 5), 20)

    # base
    #draw.polygon(screen, (0, 0, 255) if robotState['alliance'] == 'BLUE' else (225, 0, 0),
    #             [(x, y - 50), (x + 120, y - 20), (x + 120, y + 15), (x, y - 15), (x - 120, y + 15), (x - 120, y - 20),
    #              (x, y - 50)])

    draw.rect(screen, (0, 0, 255) if robotState['alliance'] == 'BLUE' else (225, 0, 0), (x - 120, y - 20, 240, 20))

def send_command(command_queue, sock, address):

    while True:
        data_out = command_queue.get()
        sock.sendto(data_out, address)


def get_data(recv_queue, sock):

    while True:
        msg = sock.recvfrom(1024)
        recv_queue.put(pickle.loads(msg))

if __name__ == '__main__':
    screen = display.set_mode((800, 450))

    init()

    pytimer = time.Clock()

    ELEVATOR_MAX_VALUE = 2195

    KEY_MODE = {K_1 : 'teleop', K_2: 'auto'}

    # text
    font = font.Font('avenir.otf', 20)
    texts = []

    can = image.load('can.png')

    can = transform.scale(can, (int(0.5 * can.get_width()), int(0.5 * can.get_height())))

    host = 'localhost' if len(sys.argv) == 2 and sys.argv[1] == 'local' else '192.168.0.100'
    port = 6969

    address = (host, port)

    print('Connecting to', address)

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

    enabled = False
    mode = 'disabled'
    start_time = 0

    last_communication = float('inf')

    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
                send_process.terminate()
                recv_process.terminate()

            if e.type == KEYDOWN:
                if e.key in KEY_MODE:

                    if not enabled:

                        print(KEY_MODE[e.key] + ' enabled')

                        enabled = True
                        mode = KEY_MODE[e.key]
                        start_time = t.time()

                    else:
                        enabled = False
                        mode = 'disabled'
                        print('Disabled')

                elif e.key == K_ESCAPE:
                    enabled = False
                    mode = 'disabled'
                    print('Disabled')

        # W - 119
        # A - 97
        # S - 115
        # D - 100
        # SPC - 32

        match_time = t.time() - start_time

        keys['R'] = key.get_pressed()[114]
        keys['F'] = key.get_pressed()[102]
        keys['W'] = key.get_pressed()[119]
        keys['A'] = key.get_pressed()[97]
        keys['S'] = key.get_pressed()[115]
        keys['D'] = key.get_pressed()[100]
        keys['SPC'] = key.get_pressed()[32]
        keys['enabled'] = enabled
        keys['mode'] = mode
        keys['drive_station_time'] = t.time()

        commands = pickle.dumps(keys)

        for k in keys:
            if keys[k] == 1:
                break

        command_queue.put(commands)

        try:
            in_data = recv_queue.get_nowait()

            if in_data:
                robotState = in_data
        except:

            robotState = {
                'elevator': 1000,
                'intake': 0,
                'ledR': 0,
                'ledG': 0,
                'ledB': 1,
                'alliance': 'RED'
            }

        if 'robot_time' in robotState:
            last_communication = t.time() - robotState['robot_time'] + robotState['robot_time_offset']

        if last_communication > 2 and match_time > 2:
            enabled = False
            mode = 'timeout disabled'

            print('Disabled due to communication timeout')



        # screen
        screen.fill((0, 0, 0))
        W = screen.get_width();
        H = screen.get_height();

        screen.blit(can, (W // 2 + 50, 50))

        # draw robot
        Robot(W // 2 - 150, 420, robotState)

        # text
        texts = ["Elevator Position: %i / %i" % (robotState['elevator'], ELEVATOR_MAX_VALUE),
                 "Enabled: %s" % mode,
                 "Network: %s" % str(address),
                 "Match Time: %f" % (match_time if enabled else 0.0),
                 "Last communication: %f" % last_communication,
                 "Connection Status: %s" % ('Connected' if last_communication < 1 else 'Disconnected')]

        for i in range(len(texts)):
            text(20, 55 + i * 30, texts[i])

        # status bar
        draw.rect(screen, (
        255 if robotState['ledR'] else 0, 255 if robotState['ledG'] else 0, 255 if robotState['ledB'] else 0),
                  (0, 0, W, 40))

        display.flip()

        pytimer.tick(60)

        display.flip()





