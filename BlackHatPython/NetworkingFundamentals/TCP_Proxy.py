#!/usr/local/bin/python3
import sys
import socket
import threading

from numpy.core import unicode


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))

    except:
        print("[*] Failed to listen on %s:%d" % (local_host, local_port))
        sys.exit(0)

    # if connected
    print("[*] Listening on %s:%d" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # local connection information
        print("[*] Receiving connection from %s:%d" % (addr[0], addr[1]))

        # start a thread to interact with the remote host
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def main():
    # usage
    if len(sys.argv[1:]) != 5:
        print("Example: python3 127.0.0.1 4444 10.10.10.1 8080 True")
        sys.exit(0)

    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # setup remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # connect our proxy and receive data before sending to host
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True

    else:
        receive_first = False

    # now spin up our listening pocket:
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # receive data from the remote if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)

        # if we have data to our local client, send it
        if len(remote_buffer):
            print("Send %d byte to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    # local -> remote -> local
    while True:
        # read from local host
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)

            # send it to our local handler
            local_buffer = request_handler(local_buffer)

            # send off the data to the remote host
            remote_socket.send(local_buffer)
            print("[*] Send to the remote host")

        # receive back the response
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[*] Received %d bytes from remote" % len(remote_buffer))
            hexdump(remote_buffer)

        # send to our response handler
        remote_buffer = response_handler(remote_buffer)

        # send the response to the local socket
        client_socket.send(remote_buffer)
        print("[*] Send to local host..")

        # if no more data on either side, close the connection
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connection...")
            break


def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in range(0, len(src), length):
        s = src[i:i + length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X %-*s %s" % (i, length * (digits + 1), hexa, text))

    print(b'\n'.join(result))


def receive_from(connection):
    buffer = " "

    # set 2 seconds timeout
    connection.settimeout(2)

    try:
        # keep reading the buffer until timeout or no more data
        while True:
            data = connection.recv(4096)

            if not data:
                break
            buffer += data

    except:
        pass

    return buffer


# packet modification
def request_handler(buffer):
    return buffer


# modified response destined for the local host
def response_handler(buffer):
    return buffer


if __name__ == '__main__':
    main()
