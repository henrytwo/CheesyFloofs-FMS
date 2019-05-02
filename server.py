import socket
import pickle
import multiprocessing

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

def processor(send, recv):


    while True:

        msg, addr = recv.get()

        # do stuff

        print(msg)

#L9u3EhzpU7

if __name__ == '__main__':
    addr = ('127.0.0.1', 25565)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(addr)

    send_queue = multiprocessing.Queue()
    recv_queue = multiprocessing.Queue()

    send_procress = multiprocessing.Process(target=send_messages, args=(send_queue, sock))
    recv_procress = multiprocessing.Process(target=recv_messages, args=(recv_queue, sock))
    command_processor = multiprocessing.Process(target=processor, args=(send_queue, recv_queue))

    send_procress.start()
    recv_procress.start()
    command_processor.start()

    print('Server running on', addr)

