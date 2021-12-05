import random
import time
from threading import Thread
from tkinter import Canvas, Tk, Button, Label


class CellType:
    """
    CellType class. It's used to be easier to check what type is a cell.
    """
    EMPTY = 0
    SNAKE = 1
    WALL = 2
    FOOD = 3
    BONUS = 4


class SnakeGame:
    """
    SnakeGame game class.
    """
    snackbar_width = 0
    offset_x = 0
    offset_y = snackbar_width

    weight = 3
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
        """
        Constructor for the Snake Game.
        :param window: The window instance
        :param canvas: The canvas to witch snake game will run
        :param config: Configuration object
        """
        self.canvas = canvas
        self.window = window
        self.rows = config['rows']
        self.columns = config['columns']
        self.width = int(canvas['width']) - self.offset_x
        self.height = int(canvas['height']) - self.offset_y
        self.box_width = self.width / self.columns
        self.box_height = self.height / self.rows

        self.board = SnakeGame.create_matrix(self.rows, self.columns)
        self.board_box = self.create_board(self.rows, self.columns)

        self.walls = config['blocks']

        # Starting message
        self.canvas_text = self.canvas.create_text(self.width / 2, self.height / 2,
                                                   fill="white", font="Calibri 20 bold", text="Press Start!")

        # Initialization
        self.snake = []
        self.food = []
        self.dir = []
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
        """
        Shows the best score then close the game.
        :return: none
        """
        if self.game_running:
            return
        self.canvas.delete(self.canvas_text)

        self.canvas_text = self.canvas.create_text(self.width / 2, self.height / 2, fill="white",
                                                   font="Calibri 20 bold", text=f'Best Score: %-3d' % self.best_score)

        thread = Thread(target=lambda: self.exit())
        thread.start()

    def exit(self):
        """
        Exit callback. It's called when the exit button is pressed.
        :return: none
        """
        time.sleep(2)
        self.window.destroy()

    def start(self):
        """
        Resets and starts the game. It initializes everything for a new game.
        :return: none
        """
        if self.game_running:
            return

        self.canvas.delete(self.canvas_text)

        self.game_running = True
        self.game_won = False
        self.game_end = False
        self.score = 0

        self.reset_matrix(self.board, CellType.EMPTY)

        # Initialising blocks
        for block in self.walls:
            self.put_on_board(block, CellType.WALL)

        self.snake = [[2, 6], [2, 5], [2, 4]]
        self.food = []

        self.put_on_board(self.snake[0], CellType.SNAKE)
        self.dir = [1, 0]

        self.spawn_food()

        if self.grid:
            self.put_grid(self.canvas, self.rows, self.columns)

        thread = Thread(target=self.pre_draw)
        thread.start()

    def pre_draw(self):
        """
        The purpose of this function is to control the game refresh rate and to show the current score
        when the game ends.
        For every game frame, the method draw() is called.
        :return: none
        """
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
        """
        It's called for every frame. It draws everything on the canvas.
        :return: none
        """
        self.draw_board()

        self.refresh_snake()
        self.move = False

    def draw_board(self):
        """
        It's called by draw() method. Changes every cell color when needed.
        :return: none
        """
        for i in range(self.rows):
            for j in range(self.columns):
                new_color = self.colors[self.board[i][j]]
                old_color = self.canvas.itemcget(self.board_box[i][j], 'fill')

                if new_color != old_color:
                    self.canvas.itemconfig(self.board_box[i][j], fill=new_color)

    def refresh_snake(self):
        """
        Moves the snake one cell with the current direction and checks for collisions.
        :return: none
        """
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

        if SnakeGame.equal_blocks(head, self.food):
            self.score += 1
            self.snake.append(old_tail)
            self.put_on_board(old_tail, CellType.SNAKE)

            self.spawn_food()

    def wall_collision(self, head_block):
        """
        Checks for wall collision.
        :param head_block: The current position of the head
        :return: true if the collision with the wall happens
        """
        i = head_block[0]
        j = head_block[1]

        return self.board[i][j] == CellType.WALL

    def snake_collision(self):
        """
        Checks for snake collision with itself.
        :return: true if the snake bytes itself
        """
        head = self.snake[0]

        # Tail collision
        for i in range(1, len(self.snake)):
            if self.equal_blocks(head, self.snake[i]):
                return True

        return False

    def block_outside(self, block):
        """
        Checks if a block(snake head) is outside board.
        :param block: The block position
        :return: true if the block it's outside the board
        """
        i = block[0]
        j = block[1]
        return i == -1 or i == self.rows or j == -1 or j == self.columns

    def update_max_score(self):
        """
        Updated the max score.
        :return: none
        """
        self.best_score = max(self.best_score, self.score)
        self.best_score_label.config(text=f'Best Score: %-3d' % self.best_score)

    @staticmethod
    def equal_blocks(block_a, block_b):
        """
        Checks if tho blocks have the same position.
        :param block_a: First block
        :param block_b: Second Block
        :return: true if the blocks have the same position
        """
        return block_a[0] == block_b[0] and block_a[1] == block_b[1]

    def put_on_board(self, block, cell_type):
        """
        Updates the blocks matrix with the respective cell type.
        :param block: The position of the block
        :param cell_type: The cell type
        :return: none
        """
        i = block[0]
        j = block[1]

        self.board[i][j] = cell_type

    def put_grid(self, canvas: Canvas, rows, columns):
        """
        Creates and shows the grid on the board game.
        :param canvas: Canvas instance
        :param rows: The number of rows
        :param columns: The number of columns
        :return: none
        """
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
        """
        Used internally to get easily the real coordinates of a block.
        :param block: The block position
        :return: (x1, y1, x2, y2) -> the coordinates of a rectangle
        """
        i = block[0]
        j = block[1]

        off_x = self.offset_x
        off_y = self.offset_y

        return off_x + j * self.box_width, off_y + i * self.box_height, off_x + (j + 1) * self.box_width, off_y + (i + 1) * self.box_height

    def create_board(self, rows, columns):
        """
        Initializes the board. It's creating a cell instance for every board block.
        :param rows: The number of rows
        :param columns: The number of columns
        :return: none
        """
        board = []

        for i in range(rows):
            board.append([])
            for j in range(columns):
                board[i].append(self.canvas.create_rectangle(self.rectangle_coords([i, j]),
                                                             fill=self.colors[CellType.EMPTY],
                                                             outline=self.colors[CellType.EMPTY], width=self.weight))

        return board

    def spawn_food(self):
        """
        Spawns the food randomly in the remaining free cells.
        :return: none
        """
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
        """
        Resets the matrix with a given value.
        :param matrix: The matrix instance
        :param value: The value
        :return: none
        """
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                matrix[i][j] = value

    @staticmethod
    def create_matrix(rows, columns, default_value=0):
        """
        Creates a matrix.
        :param rows: The number of rows
        :param columns: The number of columns
        :param default_value: The default value to be initialized with
        :return: the new matrix
        """
        a = []
        for i in range(rows):
            a.append(SnakeGame.create_list(columns, default_value))

        return a

    @staticmethod
    def create_list(length, default_value=0):
        """
        Creates a list with a given length.
        :param length: The length
        :param default_value: The value
        :return: the new list instance
        """
        v = []
        for i in range(length):
            v.append(default_value)

        return v

    def left(self):
        """
        The callback function when the player press the left arrow key. It also check for the move validity.
        :return: none
        """
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
        """
        The callback function when the player press the right arrow key. It also check for the move validity.
        :return: none
        """
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
        """
        The callback function when the player press the up arrow key. It also check for the move validity.
        :return: none
        """
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
        """
        The callback function when the player press the down arrow key. It also check for the move validity.
        :return: none
        """
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if i != -1:
            self.move = True
            i = 1
            j = 0

        self.dir = [j, i]
