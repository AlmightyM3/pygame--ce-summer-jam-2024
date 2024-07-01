import pygame

class Window:
    def __init__(self, name, size):
        self.size = size
        self.DT = 1.0
        self.name = name
        pygame.init()
        self.pgWindow = pygame.display.set_mode(size)
        pygame.display.set_caption(f"{name} | dt:{self.DT}, fps:{1000/self.DT}")
        self.clock = pygame.time.Clock()
        self.run = True

    def update(self, inputCallback):
        if not self.run:
            print("Update window has been called but run is false.")
            return
        
        pygame.display.flip()
        pygame.display.set_caption(f"{self.name} | dt:{self.DT}, fps:{(1000/self.DT):.2f}")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.run = False
                pygame.quit()
                return
            else:
                inputCallback(event)
        
        self.DT = self.clock.tick(60)