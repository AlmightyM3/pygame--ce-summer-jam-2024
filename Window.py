import pygame

class Window:
    def __init__(self, name, size):
        self.size = size
        pygame.init()
        self.pgWindow = pygame.display.set_mode(size)
        pygame.display.set_caption(name)
        self.clock = pygame.time.Clock()
        self.run = True

    def update(self, inputCallback):
        if not self.run:
            print("Update window has been called but run is false.")
            return
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.run = False
                pygame.quit()
            else:
                inputCallback(event)