import tkinter as tk
from game.game import Game
from game.json_reader import JsonReader


def main():
    config = JsonReader.read('configuration.json')

    window = tk.Tk()
    window.title('Snake')

    canvas = tk.Canvas(window, bg="#202020", width=config['width'], height=config['height'])
    canvas.grid(row=0, column=0, columnspan=3)

    game = Game(window, canvas, config)

    window.mainloop()


if __name__ == '__main__':
    main()


