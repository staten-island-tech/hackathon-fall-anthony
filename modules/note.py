import pygame.gfxdraw

NOTE_RADIUS = 45
WHITE = (255, 255, 255)

class Note:
    def __init__(self, x, y, expand_speed, id=None):
        self.id = id
        self.x = x
        self.y = y
        self.progress = 0
        self.expand_speed = expand_speed
        self.stay_timer = 0
        self.expanding = True

    def expand(self):
        if self.expanding:  # Expand inner circle until it reaches the outer circle
            self.progress += self.expand_speed
            if self.progress >= NOTE_RADIUS:
                self.expanding = False
        else:  # Shrink inner circle until it disappears
            self.progress -= self.expand_speed
            if self.progress <= 0:
                self.progress = 0

    def draw(self, screen):
        # Anti-aliasing for higher-quality shapes
        pygame.gfxdraw.aacircle(screen, self.x, self.y, NOTE_RADIUS, WHITE)
        pygame.gfxdraw.filled_circle(screen, self.x, self.y, int(self.progress), WHITE)