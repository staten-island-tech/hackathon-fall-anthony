import pygame

SCREEN_WIDTH = 800
GRAY = (200, 200, 200)

class Effect:
    def __init__(self, y):
        self.y = y
        self.alpha = 255

    def update(self):
        self.alpha -= 15
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, screen):
        effect_surface = pygame.Surface((SCREEN_WIDTH, 5))
        effect_surface.set_alpha(self.alpha)
        effect_surface.fill(GRAY)
        screen.blit(effect_surface, (0, self.y))