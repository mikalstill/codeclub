#!/usr/bin/python


import json
import random
import select
import socket
import sys

import tkinter


PORT = 5005
client_address = None
listen_socket = None
client_socket = None

GRID_SIZE = 60


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

    if client_socket:
        line = chat_text.get().rstrip()
        packet = {'type': 'chat',
                  'data': line}
        client_socket.send(json.dumps(packet).encode())

        history.insert(tkinter.END, '  Us >> %s\n' % line)
        history.see(tkinter.END)
    
        chat_text.delete(0, len(line))
    else:
        history.insert(tkinter.END, 'App  :: No one is connected!\n')
        history.see(tkinter.END)
    

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
                       'App  :: Accepted connection from %s\n' % (client_addr,))
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
        r = client_socket.recv(1024)
        if len(r) == 0:
            print('Connection lost!')
            sys.exit(1)

        packet = json.loads(r.decode())
        if packet['type'] == 'chat':
            history.insert(tkinter.END,
                           'Them << %s\n' % packet['data'].rstrip())
            history.see(tkinter.END)
    
    root.after_idle(current_processor)


previous_motion = None
previous_ship = None

def find_ship(canvas, event):
    clicked = canvas.find_overlapping(event.x, event.y,
                                        event.x, event.y)
    for obj in clicked:
        for tag in canvas.gettags(obj):
            if tag.startswith('ship'):
                return tag

    return None


def canvas_click(event):
    global canvas
    global previous_motion
    global previous_ship

    if event.type == '4':
        # Click
        previous_ship = None
        ship = find_ship(canvas, event)

        if event.num == 1 and ship:
            previous_ship = ship
            canvas.itemconfig(previous_ship, fill='red')
        elif event.num == 3 and ship:
            # Rotate the selected ship
            x1, y1, x2, y2 = canvas.coords(ship)
            width = x2 - x1
            height = y2 - y1
            canvas.coords(ship, x1, y1, x1 + height, y1 + width)
            

    elif event.type == '6' and previous_ship:
        # Mouse drag event, move a ship
        if previous_motion:
            x_delta = event.x - previous_motion[0]
            y_delta = event.y - previous_motion[1]
            history.insert(tkinter.END, 'Move %d, %s\n'
               %(x_delta, y_delta))
            canvas.move(previous_ship, x_delta, y_delta)
        previous_motion = [event.x, event.y]

    elif event.type == '5' and previous_ship:
        # Mouse release, change color back and "snap" to grid
        x, y, _, _ = canvas.coords(previous_ship)
        x_miss = x % GRID_SIZE
        y_miss = y % GRID_SIZE

        if x_miss < GRID_SIZE / 2:
            x_move = -x_miss
        else:
            x_move = GRID_SIZE - x_miss

        if y_miss < GRID_SIZE / 2:
            y_move = -y_miss
        else:
            y_move = GRID_SIZE - y_miss

        canvas.move(previous_ship, x_move + 1, y_move + 1)
        canvas.itemconfig(previous_ship, fill='blue')
        previous_motion = None
        previous_ship = None


# Our main window
root = tkinter.Tk()

canvas = tkinter.Canvas(root,
                        width=(GRID_SIZE * 10 + 2),
                        height=(GRID_SIZE * 10 + 2))
canvas.bind('<Button-1>', canvas_click)
canvas.bind('<Button-3>', canvas_click)
canvas.bind('<B1-Motion>', canvas_click)
canvas.bind('<ButtonRelease-1>', canvas_click)
canvas.pack()

history = tkinter.Text(root, height=10, width=80)
history.pack(padx=5)

chat_text = tkinter.Entry(root, width=68)
chat_text.pack(padx=5)
        
send_button = tkinter.Button(root, text='Send', command=send_chat)
send_button.pack(padx=5)
root.update()

# Draw a grid on the canvas area
for x in range(0, 10):
    for y in range(0, 10):
        canvas.create_rectangle(1 + x * GRID_SIZE,
                                1 + y * GRID_SIZE,
                                1 + x * GRID_SIZE + GRID_SIZE,
                                1 + y * GRID_SIZE + GRID_SIZE,
                                tag='%d,%d' %(x, y))

# Place ships
count = 1
for size in [2, 3, 3, 4, 5]:
    canvas.create_rectangle(1 * GRID_SIZE + 1,
                            count * GRID_SIZE + 1,
                            1 * GRID_SIZE + 1 + size * GRID_SIZE,
                            count * GRID_SIZE + 1 + GRID_SIZE,
                            fill='blue',
                            tag='ship%d' % count)
    count += 1
        

# Ask if we're a server or a client
d = ServerOrClientDialog(root)
root.wait_window(d.top)

if client_address == 'server':
    history.insert(tkinter.END, 'App  :: Running a server\n')

    listen_socket = socket.socket()
    # Allow us to reuse the same port number immediately, for easier testing:
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(('0.0.0.0', PORT))
    listen_socket.listen(5)

    history.insert(tkinter.END, 'App  :: Waiting for a connection...\n')
    current_processor = process_waiting_for_connection
else:
    history.insert(tkinter.END, 'App  :: Connecting to %s\n' % client_address)
    client_socket = socket.socket()
    client_socket.connect((client_address, PORT))
    current_processor = process_have_connection

root.after_idle(current_processor)
root.mainloop()
