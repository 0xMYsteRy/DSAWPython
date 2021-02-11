import socket

host = "127.0.0.1"
port = 80

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
print("Sending some data: ")
s.sendto(("AAAABBBB").encode(),(host, port))

# receive some data
res = s.recvfrom(4096)

print(res)