import random
import threading
import time
from threading import Thread
from tkinter import Canvas, Tk, Button, Label


class CellType:
    EMPTY = 0
    SNAKE = 1
    WALL = 2
    FOOD = 3
    BONUS = 4


class Game:
    snackbar_width = 0
    offset_x = 0
    offset_y = snackbar_width

    refresh_rate = 20
    frame_count = 0
    colors = {CellType.EMPTY: '#202020', CellType.SNAKE: '#ffffff', CellType.WALL: '#3862ab',
              CellType.FOOD: '#f54545', CellType.BONUS: '#9e36d6'}

    move = False
    game_won = False
    game_end = False
    game_running = False

    score = 0
    best_score = 0

    def __init__(self, window: Tk, canvas: Canvas, config):
        self.canvas = canvas
        self.window = window
        self.rows = config['rows']
        self.columns = config['columns']
        self.width = int(canvas['width']) - self.offset_x
        self.height = int(canvas['height']) - self.offset_y
        self.box_width = self.width / self.columns
        self.box_height = self.height / self.rows

        self.board = Game.create_matrix(self.rows, self.columns)
        self.board_box = self.create_board(self.rows, self.columns)

        self.walls = config['blocks']

        # Starting message
        self.canvas_text = self.canvas.create_text(self.width / 2, self.height / 2,
                                                   fill="white", font="Calibri 20 bold", text="Press Start!")

        # Initialization
        self.snake = [[2, 3], [2, 2], [2, 1]]
        self.food = []
        self.dir = [1, 0]
        self.board_box = self.create_board(self.rows, self.columns)

        self.grid = config['grid']

        if self.grid:
            self.put_grid(self.canvas, self.rows, self.columns)

        # Controls
        self.window.bind('<Left>', lambda e: self.left())
        self.window.bind('<Right>', lambda e: self.right())
        self.window.bind('<Up>', lambda e: self.up())
        self.window.bind('<Down>', lambda e: self.down())

        # Snackbar
        self.best_score_label = Label(self.window, text=f'Best Score: %-3d' % self.best_score)
        self.best_score_label.grid(row=1, column=1)

        self.canvas.create_rectangle(0, 0, self.width, self.snackbar_width,
                                     fill=self.colors[CellType.EMPTY], outline='')

        Button(self.window, text='Start!', bd='5', command=lambda: self.start()).grid(row=1, column=0)
        Button(self.window, text='Exit!', bd='5', command=lambda: self.on_exit()).grid(row=1, column=2)

    def on_exit(self):
        if self.game_running:
            return
        self.canvas.delete(self.canvas_text)

        self.canvas_text = self.canvas.create_text(self.width / 2, self.height / 2, fill="white",
                                                   font="Calibri 20 bold", text=f'Best Score: %-3d' % self.best_score)

        thread = Thread(target=lambda: self.exit())
        thread.start()

    def exit(self):
        time.sleep(2)
        self.window.destroy()

    def start(self):
        if self.game_running:
            return

        self.canvas.delete(self.canvas_text)

        self.game_running = True
        self.game_won = False
        self.game_end = False

        self.reset_matrix(self.board, CellType.EMPTY)

        # Initialising blocks
        for block in self.walls:
            self.put_on_board(block, CellType.WALL)

        self.snake = [[2, 3], [2, 2], [2, 1]]
        self.food = []

        self.put_on_board(self.snake[0], CellType.SNAKE)
        self.dir = [1, 0]

        self.spawn_food()

        if self.grid:
            self.put_grid(self.canvas, self.rows, self.columns)

        thread = Thread(target=self.pre_draw)
        thread.start()

    def pre_draw(self):
        while True:
            if self.game_end or self.game_won:
                self.update_max_score()
                break

            self.draw()
            self.frame_count += 1
            time.sleep(1 / self.refresh_rate)

        self.canvas_text = self.canvas.create_text(self.width / 2, self.height / 2, fill="white",
                                                   font="Calibri 20 bold", text=f'Your Score: %-3d' % self.score)
        self.game_running = False

        self.reset_matrix(self.board, CellType.EMPTY)
        self.draw_board()

    def draw(self):

        self.draw_board()

        self.refresh_snake()
        self.move = False

    def draw_board(self):
        for i in range(self.rows):
            for j in range(self.columns):
                new_color = self.colors[self.board[i][j]]
                old_color = self.canvas.itemcget(self.board_box[i][j], 'fill')

                if new_color != old_color:
                    self.canvas.itemconfig(self.board_box[i][j], fill=new_color)

    def refresh_snake(self):
        old_tail = self.snake[len(self.snake) - 1]

        new_block = [self.snake[0][0] + self.dir[1], self.snake[0][1] + self.dir[0]]

        # Check outside
        if self.block_outside(new_block) or self.wall_collision(new_block):
            self.game_end = True
            return

        self.snake.remove(old_tail)

        self.snake.insert(0, new_block)

        self.put_on_board(old_tail, CellType.EMPTY)
        self.put_on_board(new_block, CellType.SNAKE)

        # Check collision
        if self.snake_collision():
            self.game_end = True
            return

        # Check for food
        head = self.snake[0]

        if Game.equal_blocks(head, self.food):
            self.score += 1
            self.snake.append(old_tail)
            self.put_on_board(old_tail, CellType.SNAKE)

            self.spawn_food()

    def wall_collision(self, head_block):
        i = head_block[0]
        j = head_block[1]

        return self.board[i][j] == CellType.WALL

    def snake_collision(self):
        head = self.snake[0]

        # Tail collision
        for i in range(1, len(self.snake)):
            if self.equal_blocks(head, self.snake[i]):
                return True

        return False

    def block_outside(self, block):
        i = block[0]
        j = block[1]
        return i == -1 or i == self.rows or j == -1 or j == self.columns

    def update_max_score(self):
        self.best_score = max(self.best_score, self.score)
        self.best_score_label.config(text=f'Best Score: %-3d' % self.best_score)

    @staticmethod
    def equal_blocks(block_a, block_b):
        return block_a[0] == block_b[0] and block_a[1] == block_b[1]

    def put_on_board(self, block, cell_type):
        i = block[0]
        j = block[1]

        self.board[i][j] = cell_type

    def put_grid(self, canvas: Canvas, rows, columns):
        color = '#151515'
        wid = 1

        box_width = self.width / columns
        box_height = self.height / rows

        off_x = self.offset_x
        off_y = self.offset_y

        for i in range(rows + 1):
            canvas.create_line(off_x + 0, off_y + box_height * i, off_x + self.width, off_y + box_height * i,
                               fill=color, width=wid)

        for j in range(columns + 1):
            canvas.create_line(off_x + box_width * j, off_y + 0, off_x + box_width * j, off_y + self.height,
                               fill=color, width=wid)

    def rectangle_coords(self, block):
        i = block[0]
        j = block[1]

        off_x = self.offset_x
        off_y = self.offset_y

        return off_x + j * self.box_width, off_y + i * self.box_height, off_x + (j + 1) * self.box_width, off_y + (i + 1) * self.box_height

    def create_board(self, rows, columns):
        board = []

        for i in range(rows):
            board.append([])
            for j in range(columns):
                board[i].append(self.canvas.create_rectangle(self.rectangle_coords([i, j]),
                                                             fill=self.colors[CellType.EMPTY],
                                                             outline=self.colors[CellType.EMPTY], width=3))

        return board

    def spawn_food(self):
        available_blocks = []

        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] == CellType.EMPTY:
                    available_blocks.append([i, j])

        if len(available_blocks) == 0:
            self.game_won = True
            self.game_end = True
            return

        random_block = random.choice(available_blocks)
        self.food = random_block

        self.put_on_board(self.food, CellType.FOOD)

    @staticmethod
    def reset_matrix(matrix, value=0):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                matrix[i][j] = value

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
