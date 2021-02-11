import socket

host = "localhost"
port = 1337

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the client
s.connect((host, port))
print("successfull connection to: " + host)

# send some data
s.send(("GET / HTTP/1.1\r\nHost: google.com\r\n\r\n").encode())

# receive some data
res = s.recv(4096)

print(res)