import sys
import socket
import getopt
import threading
import subprocess

# define some global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print("Welcome to the World of MYsteRy!")
    print("Usage: python3 netcat.py -t target_host -p port")
    print("[*] -l | --listen                  | listen on [host:port] for incoming connections")
    print("[*] -e | --execute=file_to_run     | execute the given file upon receiving the connection")
    print("[*] -c | --command                 | initialize a command shell")
    print("[*] -u | --upload=destination      | upon receiving a connection upload a file and write to destination")
    print("Examples: ")
    print("$python3 netcat.py -t 192.168.0.1 -p 1234 -l -c")
    print("$python3 netcat.py -t 192.168.0.1 -p 1234 -l -u=c:\\target.exe")
    print("$python3 netcat.py -t 192.168.0.1 -p 1234 -l -e=\"cat /etc/passwd\"")
    sys.exit(0)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # read the command line option
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer)

    if listen:
        server_loop()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect to the target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:

            # wait for the data
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response)

            # wait for more inputs
            buffer = input("")
            buffer += "\n"

            # send if off
            client.send(buffer)

    except:
        print("[*] Excepting catch! Existing!")
        client.close()


def server_loop():
    global target

    # we listen on all interface if no special target is defined
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Run multithreading for our clients
        client_threading = threading.Thread(target=client_handler, args=(client_socket,))
        client_threading.start()


def run_command(command):
    # trim the new line
    command = command.rstrip()

    # run the command and retrive the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # heck for upload
    if len(upload_destination):

        # read in all of the bytes and write to the destination
        file_buffer = ""

        # read the data when non available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer.encode())
            file_descriptor.close()

        except:
            client_socket.send("Failed to save file to %s \r\n" % upload_destination)

        # check for command execution
        if len(execute):
            # run the command
            output = run_command(execute)
            client_socket.send(output)

        # if command shell was requested
        if command:
            while True:
                # show a simple prompt
                client_socket.send("$: ")

                cmd_buffer = ""

                while "\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024)

                # send back a command output
                response = run_command(cmd_buffer)

                # send back the response
                client_socket.send(response)


if __name__ == main():
    main()
