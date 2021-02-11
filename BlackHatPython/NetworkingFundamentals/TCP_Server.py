import socket
import threading

bind_ip = "localhost"
bind_port = 1337

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))
server.listen(5)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))


def handle_client(client_socket):
    # printout what client sends
    req = client_socket.recv(1024)
    print("[*] Received: %s" % req)

    # send back a packet
    client_socket.send("ACK!")

    client_socket.close()


while True:
    client, addr = server.accept()
    print("[*] Accept connection from : %s %d" % (addr[0], addr[1]))

    # multithreading to handle incoming data
    client_handle = threading.Thread(target=handle_client(), args=(client,))
    client_handle.start()
