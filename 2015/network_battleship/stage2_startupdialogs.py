#!/usr/bin/python


import datetime
import select
import socket
import sys

import tkinter


PORT = 5005
client_address = None
listen_socket = None
client_socket = None


class ServerOrClientDialog:
    def __init__(self, parent):
        self.top = tkinter.Toplevel(parent)

        tkinter.Label(
              self.top,
              text=('Welcome to network battleship. Would you like to '
                    'run a server, or connect to an existing server?')).pack()
        server_button = tkinter.Button(self.top, text='Run a new server',
                                       command=self.server)
        server_button.pack(pady=5)

        tkinter.Label(
              self.top,
              text=('Please specify the name or IP address of the server '
                    'to connect to:')).pack()

        self.server_location = tkinter.Entry(self.top)
        self.server_location.pack(padx=5)
        client_button = tkinter.Button(self.top, text='Connect to server',
                                       command=self.client)
        client_button.pack(pady=5)

    def server(self):
        global client_address
        client_address = 'server'
        self.top.destroy()

    def client(self):
        global client_address
        client_address = self.server_location.get()
        self.top.destroy()


def send_chat():
    global chat_text
    global client_socket

    line = chat_text.get()
    client_socket.send(line.encode())

    history.insert(tkinter.END, '  Us >> %s\n' % line.rstrip())
    history.see(tkinter.END)
    
    chat_text.set('')
    

def process_waiting_for_connection():
    # Our event processor when we don't have a connection yet

    global client_socket
    global listen_socket
    global root
    global history
    global current_processor

    readable, _, errors = select.select([listen_socket], [], [listen_socket], 0)
    if errors:
        print('Connection lost!')
        sys.exit(1)

    if readable:
        client_socket, client_addr = listen_socket.accept()
        history.insert(tkinter.END,
                       'Accepted connection from %s\n' % (client_addr,))
        current_processor = process_have_connection

    root.after_idle(current_processor)


def process_have_connection():
    # Our event processor when we do have a connection
    
    global client_socket
    global root
    global history
    global current_processor

    readable, _, errors = select.select([client_socket], [], [client_socket], 0)
    if errors:
        print('Connection lost!')
        sys.exit(1)

    if readable:
        line = client_socket.recv(1024).decode()
        if len(line) == 0:
            print('Connection lost!')
            sys.exit(1)

        history.insert(tkinter.END, 'Them << %s\n' % line.rstrip())
        history.see(tkinter.END)
    
    root.after_idle(current_processor)


# Our main window
root = tkinter.Tk()
history = tkinter.Text(root, height=30, width=80)
history.pack(padx=5)

chat_text = tkinter.Entry(root, width=70)
chat_text.pack(padx=5)
        
send_button = tkinter.Button(root, text='Send', command=send_chat)
send_button.pack(padx=5)
root.update()

# Ask if we're a server or a client
d = ServerOrClientDialog(root)
root.wait_window(d.top)

if client_address == 'server':
    history.insert(tkinter.END, 'Running a server\n')

    listen_socket = socket.socket()
    # Allow us to reuse the same port number immediately, for easier testing:
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(('0.0.0.0', PORT))
    listen_socket.listen(5)

    history.insert(tkinter.END, 'Waiting for a connection...\n')
    current_processor = process_waiting_for_connection
else:
    history.insert(tkinter.END, 'Connecting to %s\n' % client_address)
    client_socket = socket.socket()
    client_socket.connect((client_address, PORT))
    current_processor = process_have_connection

root.after_idle(current_processor)
root.mainloop()
