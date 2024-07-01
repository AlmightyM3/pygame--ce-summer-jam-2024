import pygame
class TimeIt:
    timer = 0
    def stopwatch(self, message=None):
        if not message:
            self.timer = pygame.time.get_ticks()
            return
        now = pygame.time.get_ticks()
        runtime = (now - self.timer) / 1000.0 + 0.001
        print(f"{message} {runtime:.3f}seconds, {(1.0 / runtime):.2f}fps.")
        self.timer = now