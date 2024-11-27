import pygame.draw

NOTE_RADIUS = 45
WHITE = (255, 255, 255)
RED = (252, 91, 91)
BLUE = (71, 169, 255)

class Note:
    def __init__(self, x, y, expand_speed, line_direction=None, id=None):
        self.id = id
        self.x = x
        self.y = y
        self.progress = 0
        self.expand_speed = expand_speed
        self.expanding = True
        # Color the note based on the line direction
        self.color = RED if line_direction == 1 else BLUE  # The line direction also determines the last boundary line touched
        self.alpha = 0  # Initial opacity

    def expand(self):
        if self.expanding:  # Expand inner circle until it reaches the outer circle
            self.progress += self.expand_speed
            self.alpha = min(255, int((self.progress / NOTE_RADIUS) * 255))  # Calculate alpha value (based on expansion progress)
            if self.progress >= NOTE_RADIUS:
                self.expanding = False
        else:
            self.progress -= self.expand_speed
            self.alpha = max(0, int((self.progress / NOTE_RADIUS) * 255))  # Calculate alpha value (based on expansion progress)
            if self.progress <= 0:
                self.progress = 0

    def draw(self, screen):
        alpha_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surface, (*self.color, min(self.alpha, 172)), (self.x, self.y), int(self.progress)) 
        screen.blit(alpha_surface, (0, 0))
        
        # If the note is expanding, decrease the radius of the outer circle from 125% to 100% its target radius. If the note is shrinking, increase the radius of the outer circle from 100% to 125% its target radius.
        outer_radius = NOTE_RADIUS * (1.25 - 0.25 * (self.progress / NOTE_RADIUS)) if self.expanding else NOTE_RADIUS * (1 + 0.25 * (1 - self.progress / NOTE_RADIUS))
        pygame.draw.circle(alpha_surface, (*WHITE, self.alpha), (self.x, self.y), int(outer_radius), 4)
        screen.blit(alpha_surface, (0, 0))