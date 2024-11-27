import pygame.draw

NOTE_RADIUS = 45
WHITE = (255, 255, 255)
RED = (248, 84, 84)
BLUE = (66, 148, 248)

class Note:
    def __init__(self, x, y, expand_speed, line_direction=None, id=None):
        self.id = id
        self.x = x
        self.y = y
        self.progress = 0
        self.expand_speed = expand_speed
        self.expanding = True
        self.color = RED if line_direction == 1 else BLUE

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
        pygame.draw.circle(screen, self.color, (self.x, self.y), int(self.progress))
        pygame.draw.circle(screen, WHITE, (self.x, self.y), NOTE_RADIUS, 4)