#!/usr/bin/python

# A simple network chat client that will form the basis of our network
# battleship game.

import selectors
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

# We need to read from two places at once, the local user and the remote
# one.
sel = selectors.DefaultSelector()
sel.register(sys.stdin, selectors.EVENT_READ)
sel.register(sock, selectors.EVENT_READ)

while True:
    for channel, events in sel.select():
        if channel.fileobj == sys.stdin:
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
