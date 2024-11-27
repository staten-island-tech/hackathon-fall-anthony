import pygame

class Button:
    'Button class for creating buttons as clickable images and handling their states'

    def __init__(self, pos, pressed_pos, size, pressed_size, default_image_path, pressed_image_path):
        self.pos = pos
        self.pressed_pos = pressed_pos
        self.size = size
        self.pressed_size = pressed_size
        self.default_image = pygame.image.load(default_image_path)
        self.pressed_image = pygame.image.load(pressed_image_path)
        self.rect = pygame.Rect(pos, size)
        self.rect_pressed = pygame.Rect(pos, pressed_size)
        self.clicked = False

    def draw(self, screen):
        image = self.pressed_image if self.clicked else self.default_image
        image = pygame.transform.scale(image, self.size if not self.clicked else self.pressed_size)
        screen.blit(image, self.pos if not self.clicked else self.pressed_pos)

    def is_clicked(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)