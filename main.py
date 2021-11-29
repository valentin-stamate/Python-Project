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

    # canvas.move(rec, -100, 0)
    # canvas.delete(rec)

    window.mainloop()


if __name__ == '__main__':
    main()


