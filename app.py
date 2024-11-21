import pygame, tkinter as tk
from tkinter import filedialog

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Load the screen and set its dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Audio Visualizer')

# Initialize Tkinter root (for file dialog)
root = tk.Tk()
root.withdraw()

clock = pygame.time.Clock()

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color_normal = (255, 255, 255)
        self.color_hover = (200, 200, 200)
        self.color_click = (169, 169, 169)  # Gray color for click effect
        self.font = pygame.font.Font('./glyphs/Galaksi.ttf', 48)
        self.clicked = False
        self.current_color = list(self.color_normal)

    def draw(self, screen):
        target_color = self.color_click if self.clicked else (self.color_hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color_normal)
        self.current_color = [int(self.current_color[i] + (target_color[i] - self.current_color[i]) * 0.1) for i in range(3)]
        
        # Draw shadow
        shadow_offset = 5 if not self.clicked else 2
        shadow_color = (50, 50, 50)
        shadow_rect = self.rect.move(0, shadow_offset)
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=self.rect.height // 4)
        
        # Draw button
        button_rect = self.rect.move(0, 0 if not self.clicked else 3)
        pygame.draw.rect(screen, self.current_color, button_rect, border_radius=self.rect.height // 4)
        
        # Draw highlight only when not clicked or hovered
        if not self.clicked and not self.rect.collidepoint(pygame.mouse.get_pos()):
            highlight_color = (255, 255, 255)
            highlight_rect = button_rect.inflate(-shadow_offset, -shadow_offset)
            pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=self.rect.height // 4, width=2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.select_sound_file()
            self.clicked = False

    def select_sound_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Sound Files", "*.wav *.mp3")])
        if file_path:
            click_sound = pygame.mixer.Sound(file_path)
            click_sound.play()

# Center the button on the screen
button_width, button_height = 350, 75
button_x = (SCREEN_WIDTH - button_width) // 2
button_y = (SCREEN_HEIGHT - button_height) // 2
button = Button(button_x, button_y, button_width, button_height, 'Select Sound')

while True:
    clock.tick(60)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        button.handle_event(event)

    button.draw(screen)
    pygame.display.flip()