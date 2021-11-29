import time
from threading import Thread
from tkinter import Canvas


class CellType:
    EMPTY = 0
    SNAKE = 1
    WALL = 2
    FOOD = 3
    BONUS = 4


class Game:
    refresh_rate = 5
    frame_count = 0
    colors = {CellType.EMPTY: '#202020', CellType.SNAKE: '#ffffff', CellType.WALL: '#3862ab',
              CellType.FOOD: '#f54545', CellType.BONUS: '#9e36d6'}

    def __init__(self, canvas: Canvas, rows, columns):
        self.canvas = canvas
        self.rows = rows
        self.columns = columns
        self.box_width = int(canvas['width']) / columns
        self.box_height = int(canvas['height']) / rows

        self.board = Game.create_matrix(rows, columns)

        self.board_box = self.create_board(rows, columns)

        self.snake = [[2, 3]]
        self.put_on_board(self.snake[0], CellType.SNAKE)

        self.dir = [0, 1]

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

        for i in range(self.rows):
            for j in range(self.columns):
                self.canvas.itemconfig(self.board_box[i][j], fill=self.colors[self.board[i][j]])

        self.refresh_snake()

    def refresh_snake(self):
        old_tail = self.snake[len(self.snake) - 1]

        new_block = [self.snake[0][0] + self.dir[1], self.snake[0][1] + self.dir[0]]

        self.snake.remove(old_tail)

        self.snake.insert(0, new_block)

        self.put_on_board(old_tail, CellType.EMPTY)
        self.put_on_board(new_block, CellType.SNAKE)

    def put_on_board(self, block, cell_type):
        i = block[0]
        j = block[1]

        self.board[i][j] = cell_type

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

    def rectangle_coords(self, block):
        i = block[0]
        j = block[1]

        return j * self.box_width, i * self.box_height, (j + 1) * self.box_width, (i + 1) * self.box_height

    def create_board(self, rows, columns):
        board = []

        for i in range(rows):
            board.append([])
            for j in range(columns):
                board[i].append(self.canvas.create_rectangle(self.rectangle_coords([i, j]),
                                                             fill=self.colors[CellType.EMPTY], outline=''))

        return board

    @staticmethod
    def create_matrix(rows, columns, default_value=0):
        a = []
        for i in range(rows):
            a.append(Game.create_list(columns, default_value))

        return a

    @staticmethod
    def create_list(length, default_value=0):
        v = []
        for i in range(length):
            v.append(default_value)

        return v
