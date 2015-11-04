#!/usr/bin/python

# A simple network chat client that will form the basis of our network
# battleship game.

import select
import socket
import sys


PORT = 5005


def prompt():
    sys.stdout.write('>> ')
    sys.stdout.flush()


print('Are we the client or the server? Enter "server" if we are the server, ')
print('otherwise the IP or name of a machine to connect to.\n')
prompt()

server = sys.stdin.readline().rstrip()
if server == 'server':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', PORT))
    s.listen(5)

    print('Waiting for a connection...')
    sock = s.accept()[0]
else:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, PORT))

prompt()

while True:
    # We need to read from two places at once, the local user and the remote
    # one. We therefore use a tiny bit of black magic here...
    readable, _, errors = select.select([sys.stdin.fileno(), sock.fileno()],
                                        [],
                                        [sys.stdin.fileno(), sock.fileno()])
    if errors:
        print('Connection lost!')
        sys.exit(0)

    for reading in readable:
        if reading == sys.stdin.fileno():
            line = sys.stdin.readline()
            sock.send(bytes(line, 'UTF-8'))
        else:
            line = sock.recv(1024)
            if len(line) == 0:
                # Reading nothing after a select means the connection is closed
                print('Connection lost!')
                sys.exit(0)

            print('\n<< %s' % line.decode('UTF-8').rstrip())

        prompt()
