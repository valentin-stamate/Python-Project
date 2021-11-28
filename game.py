import time
from threading import Thread
from tkinter import Canvas
import tkinter as tk


class Game:
    refresh_rate = 24
    frame_count = 0

    def __init__(self, canvas: Canvas, rows, columns):
        self.canvas = canvas
        self.rows = rows
        self.columns = columns

        Game.put_grid(self.canvas, rows, columns)

    def start(self):
        thread = Thread(target=self.pre_draw)
        thread.start()

    def pre_draw(self):
        while True:
            self.draw()
            self.frame_count += 1
            time.sleep(1 / self.refresh_rate)

    def draw(self):
        print(self.frame_count)


    @staticmethod
    def put_grid(canvas: Canvas, rows, columns):
        color = '#ffffff'
        wid = 1

        width = canvas['width']
        height = canvas['height']

        box_width = int(width) / columns
        box_height = int(height) / rows

        for i in range(rows + 1):
            canvas.create_line(0, box_height * i, width, box_height * i, fill=color, width=wid)

        for j in range(columns + 1):
            canvas.create_line(box_width * j, 0, box_width * j, height, fill=color, width=wid)

