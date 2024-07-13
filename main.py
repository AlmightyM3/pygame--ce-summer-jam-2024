import math, os, pygame, opensimplex, numpy as np
from random import randint, uniform, choice
from pygame import Vector2, Vector3
from Window import Window
from PIL import Image


NOISE_SCALE = 18
WINDOW_SIZE = Vector2(1200,800)
WINDOW_SIZE2 = WINDOW_SIZE//2
STAR_RANGE = WINDOW_SIZE*4
STAR_RANGE2 = WINDOW_SIZE*2
MIN_RADIUS = 45
MAX_RADIUS = 70
MULTI_THREAD = True
PLAYER_ACCEL = 0.5
PLAYER_VELO_MAX = 1.4
PLAYER_DECEL = 0.005
TARGET_FUEL = 5000

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
            self.velocity = (self.velocity+(pygame.mouse.get_pos()-WINDOW_SIZE2).clamp_magnitude(PLAYER_ACCEL*window.DT)).clamp_magnitude(PLAYER_VELO_MAX)
        else:
            self.velocity *= (1-PLAYER_DECEL*window.DT)
        self.pos += self.velocity*window.DT

class Star:
    def __init__(self):
        self.pos = Vector3(randint(int(-STAR_RANGE2.x), int(STAR_RANGE2.x)), randint(int(-STAR_RANGE2.x), int(STAR_RANGE2.x)), uniform(1,4))
    
    def render(self):
        pos2D = Vector2((self.pos.x-player.pos.x+STAR_RANGE2.x)%STAR_RANGE.x-STAR_RANGE2.x, (self.pos.y-player.pos.y+STAR_RANGE2.y)%STAR_RANGE.y-STAR_RANGE2.y) / self.pos.z + WINDOW_SIZE2
        pygame.draw.circle(window.pgWindow, (255,255,255), pos2D, 10/self.pos.z)

#timer = TimeIt()
class Planet:
    def __init__(self, startPos, noise):
        self.primaryColor = (randint(1,255), randint(1,255), randint(1,255))
        self.secondaryColor = (randint(1,255), randint(1,255), randint(1,255))
        
        self.radius = randint(MIN_RADIUS, MAX_RADIUS)
        self.pos = startPos-Vector2(self.radius)
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

class Enemy:
    def __init__(self, startPos, homePos, moveingImg, stopedIng):
        self.pos = startPos+Vector2()
        self.moveingImg = moveingImg
        self.stopedImg = stopedIng
        self.velocity = Vector2()
        self.homePos = homePos+Vector2()
        self.mode = 0

    def render(self):
        if self.mode<2:
            angle = int(math.degrees(-math.atan2(player.pos.y - self.pos.y, player.pos.x - self.pos.x)))-90
        else:
            angle = int(math.degrees(-math.atan2(self.homePos.y - self.pos.y, self.homePos.x - self.pos.x)))-90
        rotatedImg = pygame.transform.rotate(self.stopedImg if self.mode == 0 else self.moveingImg, angle)
        window.pgWindow.blit(rotatedImg, self.pos+WINDOW_SIZE2-(rotatedImg.get_rect().center)-player.pos)
    
    def update(self):
        if (player.pos-self.homePos).magnitude_squared() < 500*500:
            self.velocity = (player.pos-self.pos).normalize()*0.04*window.DT
            self.mode = 1
            if (player.pos-self.pos).magnitude_squared() < 50*50:
                global lives
                lives -= 1
                enemys.remove(self)
        elif (self.pos-self.homePos).magnitude_squared() > MIN_RADIUS*MIN_RADIUS:
            self.velocity = (self.homePos-self.pos).normalize()*0.04*window.DT
            self.mode = 2
        else:
            self.velocity = Vector2()
            self.mode = 0
        #print(self.mode)
        self.pos += self.velocity*window.DT


import threading 
def genPlanets():
    global planets
    r = range(-13000, 13000, 1300)
    
    if MULTI_THREAD:
        def subGenPlanets(rx,ry, main):
            for x in rx:
                for y in ry:
                    pos = Vector2(x+randint(-400,400),y+randint(-400,400))
                    planets.append(Planet(pos, choice(noiseImgs)))
                    enemys.append(Enemy(pos,pos,enemyMoveingImg2, enemyStopedImg1))
                if main:
                    window.pgWindow.fill((0,255,0), rect=pygame.Rect((100,WINDOW_SIZE.y-150),((WINDOW_SIZE.x-200)*((rx.index(x)+1)/len(rx)), 50)))
                    window.update(input)
                if not window.run:
                    return
        t1 = threading.Thread(target=subGenPlanets, args=(r[:len(r)//2], r[:len(r)//2], False))
        t2 = threading.Thread(target=subGenPlanets, args=(r[len(r)//2+1:], r[:len(r)//2], False))
        t3 = threading.Thread(target=subGenPlanets, args=(r[:len(r)//2], r[len(r)//2+1:], False))
        t1.start()
        t2.start()
        t3.start()
        subGenPlanets(r[len(r)//2+1:], r[len(r)//2+1:], True)
        t1.join()
        t2.join()
        t3.join()
    else:
        for x in r:
            for y in r:
                pos = Vector2(x+randint(-400,400),y+randint(-400,400))
                planets.append(Planet(pos, choice(noiseImgs)))
                enemys.append(Enemy(pos,pos,enemyMoveingImg2, enemyStopedImg1))
            window.update(input)
            window.pgWindow.fill((0,255,0), rect=pygame.Rect((100,WINDOW_SIZE.y-150),((WINDOW_SIZE.x-200)*((r.index(x)+1)/len(r)), 50)))
            if not window.run:
                return

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
    pygame.mixer.init()
    pygame.mixer.music.load(f"{dirPath}/loading.mp3")
    pygame.mixer.music.play()
    player = Player(Vector2(0,0), 1/32, "/SpaceshipOn.png", "/Spaceship.png")
    stars = [Star() for i in range(300)]
    planets = []
    noiseImgs = os.listdir(f"{dirPath}/noise")
    if not noiseImgs:
        genNoise(32)
        noiseImgs = os.listdir(f"{dirPath}/noise")

    noiseImgs = [np.add(np.multiply(np.array(Image.open(f"{dirPath}/noise/{i}")), 2), -1) for i in noiseImgs]
    
    enemyStopedImg1 = pygame.transform.scale_by(pygame.image.load(dirPath+"/EvilSpaceship3.png"), 1/24).convert_alpha()
    enemyMoveingImg2 = pygame.transform.scale_by(pygame.image.load(dirPath+"/EvilSpaceship3On.png"), 1/24).convert_alpha()
    enemys = []#Enemy(Vector2(500,500),enemyMoveingImg2, enemyStopedImg1)
    
    genPlanets()

    fuelIcon = pygame.transform.scale_by(pygame.image.load(dirPath+"/Fuel.png"), 1/24).convert_alpha()
    lifeIcon = pygame.transform.scale_by(pygame.image.load(dirPath+"/Lives.png"), 1/24).convert_alpha()
    winPlayer = pygame.transform.scale_by(pygame.image.load(dirPath+"/SpaceshipFacingCameraOn.png"), 1/32).convert_alpha()
    
    if window.run:
        pygame.mixer.music.set_volume(0.83)
        pygame.mixer.music.load(f"{dirPath}/mainTheme.mp3")
        pygame.mixer.music.play()

    lives = 3
    progress = 0.0

    while window.run:
        if lives < 0:
            pygame.mixer.music.stop() 
            window.update(input)
            continue
        elif progress >= TARGET_FUEL:
            window.pgWindow.fill((0,0,0))
            for star in stars:
                star.pos = Vector3(star.pos.x, star.pos.y,(star.pos.z+window.DT/500)%4)
                star.render()
            window.pgWindow.blit(winPlayer, WINDOW_SIZE2-winPlayer.get_rect().center)
            window.update(input)
            continue
        player.update()
        for enemy in enemys:
            enemy.update()

        onPlanet = False
        for planet in planets:
            if (player.pos-planet.pos-Vector2(planet.radius)).magnitude_squared() <= planet.radius*planet.radius*4:
                onPlanet = True
                if uniform(0,1)>0.95:
                    angle = uniform(0,math.pi*2)
                    enemys.append(Enemy(planet.pos+Vector2(math.cos(angle)*MAX_RADIUS*7, math.sin(angle)*MAX_RADIUS*7),planet.pos,enemyMoveingImg2, enemyStopedImg1))
                break
        if onPlanet:
            progress+=window.DT
            if progress >= TARGET_FUEL:
                pygame.mixer.music.set_volume(1)
                pygame.mixer.music.load(f"{dirPath}/LevelComplete.mp3")
                pygame.mixer.music.play()

        window.pgWindow.fill((0,0,0))
        for star in stars:
            star.render()
        for planet in planets:
            planet.render()
        for enemy in enemys:
            enemy.render()
        player.render()

        window.pgWindow.fill((255,0,255), rect=pygame.Rect((85,45),((WINDOW_SIZE.x-190), 60)))
        window.pgWindow.fill((0,0,0), rect=pygame.Rect((90,50),((WINDOW_SIZE.x-200), 50)))
        window.pgWindow.fill((255,0,255), rect=pygame.Rect((90,50),((WINDOW_SIZE.x-200)*((progress)/TARGET_FUEL), 50)))
        window.pgWindow.blit(fuelIcon, Vector2(55,80)-fuelIcon.get_rect().center)
        for i in range(lives):
            window.pgWindow.blit(lifeIcon, Vector2(WINDOW_SIZE.x-60,80+i*75)-lifeIcon.get_rect().center)
        window.update(input)
