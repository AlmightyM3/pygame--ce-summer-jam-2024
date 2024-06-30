import pygame
from Window import Window

WINDOW_SIZE = (600,600)

if __name__ == "__main__":
    def input(input):
        pass
            
    window = Window("It works?", WINDOW_SIZE)

    while window.run:
        window.update(input)
