# And a ball!

import random
import time

from tkinter import *


WINDOW_HEIGHT = 500
WINDOW_WIDTH = 800

PADDLE_SIZE = 100
PADDLE_SPEED = 10

BALL_SIZE = 20
BALL_SPEED = 3


class game:
    def __init__(self):
        self.root = Tk()
        self.root.bind('<Key>', self.keypress)

        self.window = Canvas(self.root,
                             width=WINDOW_WIDTH,
                             height=WINDOW_HEIGHT)
        self.window.pack()

        # Paddles
        paddle_left = (WINDOW_WIDTH - PADDLE_SIZE) / 2
        self.paddle_direction = {}
        self.window.create_rectangle(paddle_left,
                                     WINDOW_HEIGHT - 30,
                                     paddle_left + PADDLE_SIZE,
                                     WINDOW_HEIGHT - 10,
                                     fill='blue', tag='paddle_one')
        self.window.create_rectangle(paddle_left,
                                     10,
                                     paddle_left + PADDLE_SIZE,
                                     30,
                                     fill='blue', tag='paddle_two')
        self.paddle_direction['paddle_one'] = 0
        self.paddle_direction['paddle_two'] = 0

        # And a ball
        self.newball()

        self.paint()
        self.root.mainloop()

    def paint(self):
        # Move paddles
        for paddle in ['paddle_one', 'paddle_two']:
            self.window.move(paddle, self.paddle_direction[paddle], 0)

        # Move ball
        self.window.move('ball',
                         self.ball_horizontal_speed,
                         self.ball_vertical_speed)

        # Redraw
        self.window.update()

        # Bounce paddles
        for paddle in ['paddle_one', 'paddle_two']:
            (x1, y1, x2, y2) = self.window.coords(paddle)
            if x1 < PADDLE_SPEED:
                self.paddle_direction[paddle] = PADDLE_SPEED
            if x2 > WINDOW_WIDTH - PADDLE_SPEED:
                self.paddle_direction[paddle] = -PADDLE_SPEED

        # Bounce ball of side walls
        (x1, y1, x2, y2) = self.window.coords('ball')
        if x1 < BALL_SPEED:
            self.ball_horizontal_speed = BALL_SPEED
        if x2 > WINDOW_WIDTH - BALL_SPEED:
            self.ball_horizontal_speed = -BALL_SPEED

        # Ball bounce of paddles
        for paddle in ['paddle_one', 'paddle_two']:
            paddle_coords = self.window.coords(paddle)
            colliding = self.window.find_overlapping(
                paddle_coords[0] - BALL_SPEED,
                paddle_coords[1] - BALL_SPEED,
                paddle_coords[2] + BALL_SPEED,
                paddle_coords[3] + BALL_SPEED)
            for obj in colliding:
                # We are giving the object id, which we need to turn back into a
                # name
                if 'ball' in self.window.gettags(obj):
                    if paddle == 'paddle_one':
                        self.ball_vertical_speed = -BALL_SPEED
                    elif paddle == 'paddle_two':
                        self.ball_vertical_speed = BALL_SPEED
                

        # Ball falls off top and bottom
        if y1 < BALL_SPEED:
            self.flash()
            self.window.delete('ball')
            self.newball()

        if y2 > WINDOW_HEIGHT - BALL_SPEED:
            self.flash()
            self.window.delete('ball')
            self.newball()

        # Schedule another paint
        self.root.after(40, self.paint)

    def newball(self):
        # Create the ball
        ball_left = (WINDOW_WIDTH - BALL_SIZE) / 2
        ball_top = (WINDOW_HEIGHT - BALL_SIZE) / 2
        self.window.create_oval(ball_left,
                                ball_top,
                                ball_left + BALL_SIZE,
                                ball_top + BALL_SIZE,
                                fill='red', tag='ball')

        # Ball direction is handled as two components to avoid a bunch of
        # trigonometric maths
        vertical_direction = random.randint(0, 99) % 2
        if vertical_direction == 0:
            self.ball_vertical_speed = BALL_SPEED
        else:
            self.ball_vertical_speed = -BALL_SPEED

        horizontal_direction = random.randint(0, 99) % 2
        if horizontal_direction == 0:
            self.ball_horizontal_speed = BALL_SPEED * 2
        else:
            self.ball_horizontal_speed = -BALL_SPEED * 2
        
    def flash(self):
        for i in range(5):
            self.window.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
                                        fill='yellow', tag='flash')
            self.window.update()
            time.sleep(0.08)
            self.window.delete('flash')
            self.window.update()
            time.sleep(0.08)
        
    def keypress(self, event):
        if event.char == 'd':
            self.paddle_direction['paddle_two'] = -PADDLE_SPEED
        elif event.char == 'f':
            self.paddle_direction['paddle_two'] = PADDLE_SPEED
        elif event.char == 'j':
            self.paddle_direction['paddle_one'] = -PADDLE_SPEED
        elif event.char == 'k':
            self.paddle_direction['paddle_one'] = PADDLE_SPEED


random.seed(time.time())
app = game()
