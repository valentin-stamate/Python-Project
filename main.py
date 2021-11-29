import tkinter as tk
from game import Game


def main():
    window = tk.Tk()
    window.title('Snake')

    canvas = tk.Canvas(window, bg="#202020", height=460, width=690)
    canvas.grid(row=0, column=0, columnspan=4)

    game = Game(window, canvas, 20, 30)

    window.bind('<Left>', lambda e: game.left())
    window.bind('<Right>', lambda e: game.right())
    window.bind('<Up>', lambda e: game.up())
    window.bind('<Down>', lambda e: game.down())

    window.mainloop()


if __name__ == '__main__':
    main()


