import math
import os
import pygame
from random import randint, uniform
from pygame import Vector2, Vector3
from Window import Window
import numpy as np

WINDOW_SIZE = Vector2(1200,800)
WINDOW_SIZE2 = WINDOW_SIZE//2
STAR_RANGE = WINDOW_SIZE*4
STAR_RANGE2 = WINDOW_SIZE*2

dirPath = os.path.dirname(os.path.abspath(__file__)).lower()
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")

class Player:
    def __init__(self, startPos, size, imgPath):
        self.pos = startPos
        self.size = size
        self.img = pygame.transform.scale(pygame.image.load(dirPath+imgPath), size).convert_alpha()

    def render(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = int(math.degrees(-math.atan2(mouse_y - WINDOW_SIZE2.y, mouse_x - WINDOW_SIZE2.x)))-90
        rotatedImg = pygame.transform.rotate(self.img, angle)
        window.pgWindow.blit(rotatedImg, WINDOW_SIZE2-(rotatedImg.get_rect().center))
    
    def update(self):
        if pygame.mouse.get_pressed()[0]:
            self.pos = self.pos+(pygame.mouse.get_pos()-WINDOW_SIZE2).clamp_magnitude(window.DT)

class Star:
    def __init__(self):
        self.pos = Vector3(randint(-STAR_RANGE2.x, STAR_RANGE2.x), randint(-STAR_RANGE2.y, STAR_RANGE2.y), uniform(1,4))
    
    def render(self):
        pos2D = Vector2((self.pos.x-player.pos.x+STAR_RANGE2.x)%STAR_RANGE.x-STAR_RANGE.x, (self.pos.y-player.pos.y+STAR_RANGE2.y)%STAR_RANGE.y-STAR_RANGE.y) / self.pos.z + WINDOW_SIZE
        pygame.draw.circle(window.pgWindow, (255,255,255), pos2D, 10/self.pos.z)

class Planet:
    def __init__(self):
        self.pos = Vector2(0,0)
        self.color = (randint(1,255), randint(1,255), randint(1,255))
        self.radius = 80
        self.surface = pygame.Surface((self.radius*2, self.radius*2))
        imgArray = np.zeros((self.radius*2, self.radius*2, 3))

        imgArray[:,:] = self.color

        r2 = self.radius*self.radius
        for x in range(-self.radius, self.radius, 1):
            for y in range(-self.radius, self.radius, 1):
                if x*x + y*y > r2:
                    imgArray[self.radius+x,self.radius+y] = (0, 0, 0)

        pygame.surfarray.blit_array(self.surface, imgArray)
        self.surface.set_colorkey((0,0,0))
    
    def render(self):
        #pygame.draw.circle(window.pgWindow, self.color, self.pos-player.pos+WINDOW_SIZE2, self.radius)
        window.pgWindow.blit(self.surface, self.pos-player.pos+WINDOW_SIZE2-Vector2(self.radius))

if __name__ == "__main__":
    def input(input):
        pass
            
    window = Window("It works?", WINDOW_SIZE)
    player = Player(Vector2(0,0), Vector2(64,64), "/player.png")
    stars = [Star() for i in range(300)]
    testPlanet = Planet()

    while window.run:
        player.update()
        
        window.pgWindow.fill((0,0,0))
        for star in stars:
            star.render()
        testPlanet.render()
        player.render()
        window.update(input)
