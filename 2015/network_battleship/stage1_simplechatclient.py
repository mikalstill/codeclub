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
    s = socket.socket()
    # Allow us to reuse the same port number immediately, for easier testing:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PORT))
    s.listen(5)

    print('Waiting for a connection...')
    sock, client_addr = s.accept()
    print('Received connection from %s' % (client_addr,))
else:
    sock = socket.socket()
    sock.connect((server, PORT))

prompt()

while True:
    # We need to read from two places at once, the local user and the remote
    # one. We therefore use a tiny bit of black magic here...
    readable, _, errors = select.select([sys.stdin, sock],
                                        [],
                                        [sys.stdin, sock])
    if errors:
        print('Connection lost!')
        sys.exit(0)

    for reading in readable:
        if reading == sys.stdin:
            line = sys.stdin.readline()
            sock.send(line.encode())
        else:
            line = sock.recv(1024).decode()
            if len(line) == 0:
                # Reading nothing after a select means the connection is closed
                print('Connection lost!')
                sys.exit(0)

            print('\n<< %s' % line.rstrip())

        prompt()
