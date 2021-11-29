import tkinter as tk
from tkinter import Canvas
from game import Game


def main():
    window = tk.Tk()
    window.title('Snake')

    canvas = tk.Canvas(window, bg="#202020", height=300, width=300)
    canvas.pack()

    game = Game(canvas, 10, 10)
    game.start()

    window.bind('<Left>', lambda e: game.left())
    window.bind('<Right>', lambda e: game.right())
    window.bind('<Up>', lambda e: game.up())
    window.bind('<Down>', lambda e: game.down())


    # canvas.move(rec, -100, 0)
    # canvas.delete(rec)

    window.mainloop()


if __name__ == '__main__':
    main()


