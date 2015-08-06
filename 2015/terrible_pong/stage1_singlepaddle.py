# A very simple pong paddle

from tkinter import *


WINDOW_HEIGHT = 500
WINDOW_WIDTH = 800

PADDLE_SIZE = 100
PADDLE_SPEED = 5


class game:
    def __init__(self):
        self.root = Tk()
        self.root.bind('<Key>', self.keypress)

        self.window = Canvas(self.root,
                             width=WINDOW_WIDTH,
                             height=WINDOW_HEIGHT)
        self.window.pack()

        paddle_left = (WINDOW_WIDTH - PADDLE_SIZE) / 2
        self.window.create_rectangle(paddle_left,
                                     WINDOW_HEIGHT - 30,
                                     paddle_left + PADDLE_SIZE,
                                     WINDOW_HEIGHT - 10,
                                     fill='blue', tag='paddle_one')
        self.paddle_direction = 0
        
        self.paint()
        self.root.mainloop()

    def paint(self):
        self.window.move('paddle_one', self.paddle_direction, 0)
        self.window.update()

        # Bounce
        (x1, y1, x2, y2) = self.window.coords('paddle_one')
        if x1 < PADDLE_SPEED:
            self.paddle_direction = PADDLE_SPEED
        if x2 > WINDOW_WIDTH - PADDLE_SPEED:
            self.paddle_direction = -PADDLE_SPEED

        # Schedule another paint
        self.root.after(40, self.paint)

    def keypress(self, event):
        if event.char == 'j':
            self.paddle_direction = -PADDLE_SPEED
        elif event.char == 'k':
            self.paddle_direction = PADDLE_SPEED


app = game()
