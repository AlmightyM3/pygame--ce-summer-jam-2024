import math, os, pygame, opensimplex, numpy as np
from random import randint, uniform, choice
from pygame import Vector2, Vector3
from Window import Window
from PIL import Image


from TimeIt import TimeIt

NOISE_SCALE = 18
WINDOW_SIZE = Vector2(1200,800)
WINDOW_SIZE2 = WINDOW_SIZE//2
STAR_RANGE = WINDOW_SIZE*4
STAR_RANGE2 = WINDOW_SIZE*2
MIN_RADIUS = 45
MAX_RADIUS = 70
MULTI_THREAD = True

dirPath = os.path.dirname(os.path.abspath(__file__)).lower()
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")

class Player:
    def __init__(self, startPos, size, moveingImgPath, stopedIngImgPath):
        self.pos = startPos
        self.size = size
        self.moveingImg = pygame.transform.scale_by(pygame.image.load(dirPath+moveingImgPath), size).convert_alpha()
        self.stopedImg = pygame.transform.scale_by(pygame.image.load(dirPath+stopedIngImgPath), size).convert_alpha()
        self.velocity = Vector2()

    def render(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = int(math.degrees(-math.atan2(mouse_y - WINDOW_SIZE2.y, mouse_x - WINDOW_SIZE2.x)))-90
        rotatedImg = pygame.transform.rotate((self.moveingImg if pygame.mouse.get_pressed()[0] else self.stopedImg), angle)
        window.pgWindow.blit(rotatedImg, WINDOW_SIZE2-(rotatedImg.get_rect().center))
    
    def update(self):
        if pygame.mouse.get_pressed()[0]:
            self.velocity = (self.velocity+(pygame.mouse.get_pos()-WINDOW_SIZE2).clamp_magnitude(0.5*window.DT)).clamp_magnitude(1.4)
        else:
            self.velocity *= 0.96
        self.pos += self.velocity*window.DT

class Star:
    def __init__(self):
        self.pos = Vector3(randint(-STAR_RANGE2.x, STAR_RANGE2.x), randint(-STAR_RANGE2.y, STAR_RANGE2.y), uniform(1,4))
    
    def render(self):
        pos2D = Vector2((self.pos.x-player.pos.x+STAR_RANGE2.x)%STAR_RANGE.x-STAR_RANGE.x, (self.pos.y-player.pos.y+STAR_RANGE2.y)%STAR_RANGE.y-STAR_RANGE.y) / self.pos.z + WINDOW_SIZE
        pygame.draw.circle(window.pgWindow, (255,255,255), pos2D, 10/self.pos.z)

#timer = TimeIt()
class Planet:
    def __init__(self, startPos, noise):
        self.pos = startPos
        self.primaryColor = (randint(1,255), randint(1,255), randint(1,255))
        self.secondaryColor = (randint(1,255), randint(1,255), randint(1,255))
        
        self.radius = randint(MIN_RADIUS, MAX_RADIUS)
        diameter = self.radius*2
        self.surface = pygame.Surface((diameter, diameter))
        imgArray = np.zeros((diameter, diameter, 3))

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
        self.surface = pygame.transform.smoothscale_by(self.surface,2)
    
    def render(self):
        #pygame.draw.circle(window.pgWindow, self.primaryColor, self.pos-player.pos+WINDOW_SIZE2, self.radius)
        window.pgWindow.blit(self.surface, self.pos-player.pos+WINDOW_SIZE2-Vector2(self.radius))

import threading 
def genPlanets():
    global planets
    r = range(-13000, 13000, 1300)
    
    if MULTI_THREAD:
        def subGenPlanets(rx,ry):
            for x in rx:
                for y in ry:
                    planets.append(Planet(Vector2(x+randint(-400,400),y+randint(-400,400)), choice(noiseImgs)))
        t1 = threading.Thread(target=subGenPlanets, args=(r[:len(r)//2], r[:len(r)//2]))
        t2 = threading.Thread(target=subGenPlanets, args=(r[len(r)//2+1:], r[:len(r)//2]))
        t3 = threading.Thread(target=subGenPlanets, args=(r[:len(r)//2], r[len(r)//2+1:]))
        t1.start()
        t2.start()
        t3.start()
        subGenPlanets(r[len(r)//2+1:], r[len(r)//2+1:])
        t1.join()
        t2.join()
        t3.join()
    else:
        for x in r:
            for y in r:
                planets.append(Planet(Vector2(x+randint(-400,400),y+randint(-400,400)), choice(noiseImgs)))

def genNoise(num):
    for i in range(num):
        opensimplex.seed(randint(0,1024))
        size = np.array(range(MAX_RADIUS+1))/NOISE_SCALE
        noise = opensimplex.noise2array(size, size)
        img = Image.fromarray(np.multiply(np.add(noise,1),1/2))
        img.save(f"{dirPath}/noise/{i}.tiff")
        print(i)


if __name__ == "__main__":
    def input(input):
        pass

    window = Window("It works?", WINDOW_SIZE)
    window.pgWindow.blit(pygame.image.load(dirPath+"/loading.png"), (0,0))
    window.update(input)
    player = Player(Vector2(0,0), 1/32, "/SpaceshipOn.png", "/Spaceship.png")
    stars = [Star() for i in range(300)]
    planets = []
    noiseImgs = os.listdir(f"{dirPath}/noise")
    if not noiseImgs:
        genNoise(32)
        noiseImgs = os.listdir(f"{dirPath}/noise")

    noiseImgs = [np.add(np.multiply(np.array(Image.open(f"{dirPath}/noise/{i}")), 2), -1) for i in noiseImgs]
    timer = TimeIt()
    timer.stopwatch()
    genPlanets()
    timer.stopwatch("Gen planets.")

    while window.run:
        player.update()
        
        window.pgWindow.fill((0,0,0))
        for star in stars:
            star.render()
        for planet in planets:
            planet.render()
        player.render()
        window.update(input)
