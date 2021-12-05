import tkinter as tk
from game.snakegame import SnakeGame
from game.json_reader import JsonReader


def main():
    config = JsonReader.read('configuration.json')

    window = tk.Tk()
    window.title('Snake')

    canvas = tk.Canvas(window, bg="#202020", width=config['width'], height=config['height'])
    canvas.grid(row=0, column=0, columnspan=3)

    SnakeGame(window, canvas, config)

    window.eval('tk::PlaceWindow . center')
    window.mainloop()


if __name__ == '__main__':
    main()


