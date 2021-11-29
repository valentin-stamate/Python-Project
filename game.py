import random
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
    refresh_rate = 7
    frame_count = 0
    colors = {CellType.EMPTY: '#202020', CellType.SNAKE: '#ffffff', CellType.WALL: '#3862ab',
              CellType.FOOD: '#f54545', CellType.BONUS: '#9e36d6'}

    move = False
    game_won = False
    game_end = False
    score = 0

    def __init__(self, canvas: Canvas, rows, columns):
        self.canvas = canvas
        self.rows = rows
        self.columns = columns
        self.box_width = int(canvas['width']) / columns
        self.box_height = int(canvas['height']) / rows

        self.board = Game.create_matrix(rows, columns)

        self.board_box = self.create_board(rows, columns)

        self.snake = [[2, 3]]
        self.food = []
        self.spawn_food()

        self.put_on_board(self.snake[0], CellType.SNAKE)

        self.dir = [1, 0]

        Game.put_grid(self.canvas, rows, columns)

    def start(self):
        thread = Thread(target=self.pre_draw)
        thread.start()

    def pre_draw(self):
        while True:
            if self.game_end or self.game_won:
                return

            self.draw()
            self.frame_count += 1
            time.sleep(1 / self.refresh_rate)

    def draw(self):

        for i in range(self.rows):
            for j in range(self.columns):
                self.canvas.itemconfig(self.board_box[i][j], fill=self.colors[self.board[i][j]])

        try:
            self.refresh_snake()
        except:
            self.game_end = True
            print("Game Ended")

        self.move = False

    def refresh_snake(self):
        old_tail = self.snake[len(self.snake) - 1]

        new_block = [self.snake[0][0] + self.dir[1], self.snake[0][1] + self.dir[0]]

        self.snake.remove(old_tail)

        self.snake.insert(0, new_block)

        self.put_on_board(old_tail, CellType.EMPTY)
        self.put_on_board(new_block, CellType.SNAKE)

        # Check for food
        head = self.snake[0]

        if Game.equal_blocks(head, self.food):
            self.score += 1

            self.snake.append(old_tail)
            self.put_on_board(old_tail, CellType.SNAKE)

            self.spawn_food()


    @staticmethod
    def equal_blocks(block_a, block_b):
        return block_a[0] == block_b[0] and block_a[1] == block_b[1]

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

    def spawn_food(self):
        available_blocks = []

        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] == CellType.EMPTY:
                    available_blocks.append([i, j])

        if len(available_blocks) == 0:
            self.game_won = True
            return

        random_block = random.choice(available_blocks)
        self.food = random_block

        self.put_on_board(self.food, CellType.FOOD)

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

    def left(self):
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if j != 1:
            self.move = True
            j = -1
            i = 0

        self.dir = [j, i]

    def right(self):
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if j != -1:
            self.move = True
            j = 1
            i = 0

        self.dir = [j, i]

    def up(self):
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if i != 1:
            self.move = True
            i = -1
            j = 0

        self.dir = [j, i]

    def down(self):
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if i != -1:
            self.move = True
            i = 1
            j = 0

        self.dir = [j, i]
