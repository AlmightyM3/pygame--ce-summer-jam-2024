import math
import os
import pygame
from random import randint, uniform
from pygame import Vector2, Vector3
from Window import Window
import numpy as np
import opensimplex # type: ignore
import threading

#from TimeIt import TimeIt

NOISE_SCALE = 18
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
        '''
        Use acceleration for the spaceship movement, use wasd movement (in addition to mouse - accelerate until you get to midpoint between mouse point and original player position, and then decelerate.)
        W and S move forwards and backwards, A and D rotate the ship. (asteroids controls)

        Make it so that the spaceship size changes as it get's closer to a planet, corresponding to the scale (planet.radius);
        '''
        if pygame.mouse.get_pressed()[0]:
            self.pos = self.pos+(pygame.mouse.get_pos()-WINDOW_SIZE2).clamp_magnitude(window.DT)

class Star:
    def __init__(self):
        self.pos = Vector3(randint(-STAR_RANGE2.x, STAR_RANGE2.x), randint(-STAR_RANGE2.y, STAR_RANGE2.y), uniform(1,4))
    
    def render(self):
        pos2D = Vector2((self.pos.x-player.pos.x+STAR_RANGE2.x)%STAR_RANGE.x-STAR_RANGE.x, (self.pos.y-player.pos.y+STAR_RANGE2.y)%STAR_RANGE.y-STAR_RANGE.y) / self.pos.z + WINDOW_SIZE
        pygame.draw.circle(window.pgWindow, (255,255,255), pos2D, 10/self.pos.z)

#timer = TimeIt()
class Planet:
    def __init__(self, startPos):
        self.pos = startPos
        self.primaryColor = (randint(1,255), randint(1,255), randint(1,255))
        self.secondaryColor = (randint(1,255), randint(1,255), randint(1,255))
        
        self.radius = randint(80, 120)
        diameter = self.radius*2
        self.surface = pygame.Surface((diameter, diameter))
        imgArray = np.zeros((diameter, diameter, 3))

        #imgArray[:,:] = self.primaryColor
        #timer.stopwatch()
        opensimplex.seed(randint(0,1024))
        size = np.array(range(self.radius+1))/NOISE_SCALE
        noise = opensimplex.noise2array(size, size)
        #timer.stopwatch("Generate noise")

        w = uniform(-0.4,0.4)
        r2 = self.radius*self.radius
        for x in range(diameter):
            for y in range(diameter):
                d2 = (x-self.radius)*(x-self.radius) + (y-self.radius)*(y-self.radius)
                if d2 < r2:
                    imgArray[x,y] = (self.secondaryColor if (noise[x//2,y//2]+noise[(x+1)//2,y//2]+noise[x//2,(y+1)//2]+noise[(x+1)//2,(y+1)//2])/4>w else self.primaryColor)
                    imgArray[x,y] *= 1-d2/r2
        #timer.stopwatch("Color, crop to circle, and shade")

        pygame.surfarray.blit_array(self.surface, imgArray)
        self.surface.set_colorkey((0,0,0))
    
    def render(self):
        #pygame.draw.circle(window.pgWindow, self.primaryColor, self.pos-player.pos+WINDOW_SIZE2, self.radius)
        window.pgWindow.blit(self.surface, self.pos-player.pos+WINDOW_SIZE2-Vector2(self.radius))

# Still not what I'd like due to the lag spikes and sometimes uneven but predictable placement. I may try pre-placing a large number of planets on a grid and then shifting them slightly to make it appear random
def tryAddPlanet():
    minDist = 1000000000000
    minPos = Vector2()
    for planet in planets:
        currentDist = (planet.pos.x-player.pos.x)*(planet.pos.x-player.pos.x) + (planet.pos.y-player.pos.y)*(planet.pos.y-player.pos.y)
        if currentDist < minDist:
            minDist = currentDist
            minPos = planet.pos

    if minDist > 1000*1000:
        planets.append(Planet(player.pos+(-minPos+player.pos).normalize()*800))

def subGenPlanets(rx, ry):
    output = []
    for x in rx:
        for y in ry:
            output.append(Planet(Vector2(x,y)))
    return output
    
def genPlanets():
    global planets
    r = range(-2400, 2400, 400)
    #subThread = threading.Thread(target=subGenPlanets, args=(r, r[:len(r)//2]))
    #subThread.start()
    #value1 = subGenPlanets(r, r[len(r)//2+1:])
    #value2 = subThread.join()
    #planets += value1+value2

    for x in r:
        for y in r:
            planets.append(Planet(Vector2(x,y)))

if __name__ == "__main__":
    def input(input):
        pass

    window = Window("It works?", WINDOW_SIZE)
    player = Player(Vector2(0,0), Vector2(64,64), "/player.png")
    stars = [Star() for i in range(300)]
    planets = []
    genPlanets()

    while window.run:
        player.update()
        #tryAddPlanet()
        
        window.pgWindow.fill((0,0,0))
        for star in stars:
            star.render()
        for planet in planets:
            planet.render()
        player.render()
        window.update(input)
