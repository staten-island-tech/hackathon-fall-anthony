import pygame, pygame.gfxdraw, sys, random, json

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pulsebound")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font("./glyphs/good_timing.otf", 64)
small_font = pygame.font.Font("./glyphs/good_timing.otf", 24)

# Game states
MENU = "menu"
GAME = "game"
PAUSE = "pause"
RESTART = "restart"
state = MENU

# Load settings and notes from notes.json
def load_notes(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data['settings'], data['notes']

settings, note_instructions = load_notes('notes.json')

# Apply settings
line_speed = settings['line_speed']
top_line_y = settings['top_line_y']
bottom_line_y = settings['bottom_line_y']
NOTE_SPEED = settings['note_speed']
NOTE_EXPAND_SPEED = settings['note_expand_speed']

# Starting line position and direction
line_y = SCREEN_HEIGHT // 2
line_direction = 1

# Define LINE_WIDTH
LINE_WIDTH = 5
NOTE_RADIUS = 45

class Note:
    def __init__(self, x, y, expand_speed):
        self.x = x
        self.y = y
        self.progress = 0
        self.expand_speed = expand_speed
        self.stay_timer = 0
        self.expanding = True
        self.opacity = 255

    def expand(self):
        if self.expanding:
            self.progress += self.expand_speed
            if self.progress >= NOTE_RADIUS:
                self.expanding = False
        else:
            self.progress -= self.expand_speed
            self.opacity = max(189, self.opacity - 5)
            if self.progress <= 0:
                self.progress = 0

    def draw(self):
        color = (WHITE[0], WHITE[1], WHITE[2], self.opacity)
        surface = pygame.Surface((NOTE_RADIUS * 2, NOTE_RADIUS * 2), pygame.SRCALPHA)
        
        # Draw thicker outline by drawing multiple concentric circles
        for i in range(3):  # Adjust the range for thicker outlines
            pygame.draw.circle(surface, color, (NOTE_RADIUS, NOTE_RADIUS), NOTE_RADIUS - i, 1)
        
        pygame.draw.circle(surface, color, (NOTE_RADIUS, NOTE_RADIUS), int(self.progress))
        screen.blit(surface, (self.x - NOTE_RADIUS, self.y - NOTE_RADIUS))

notes = []

def draw_game():
    global line_y, line_direction, line_speed
    screen.fill(BLACK)
    pygame.draw.line(screen, WHITE, (0, top_line_y), (SCREEN_WIDTH, top_line_y), 10)
    pygame.draw.line(screen, WHITE, (0, bottom_line_y), (SCREEN_WIDTH, bottom_line_y), 10)
    pygame.draw.line(screen, GRAY, (0, line_y), (SCREEN_WIDTH, line_y), LINE_WIDTH)
    
    line_y += line_speed * line_direction
    if line_y <= top_line_y or line_y >= bottom_line_y:
        line_direction *= -1
        line_y = max(min(line_y, bottom_line_y), top_line_y)

    for note in notes:
        note.expand()
        note.draw()
        if note.progress <= 0 and note.opacity <= 38:
            notes.remove(note)

def pause_game():
    global state
    state = PAUSE

def restart_game():
    global state, notes, line_y, line_direction, line_speed, note_timer, note_index
    state = GAME
    notes = []
    line_y = SCREEN_HEIGHT // 2
    line_direction = 1
    line_speed = settings['line_speed']
    note_timer = 0
    note_index = 0

def rewind_game():
    global note_timer, note_index
    note_timer = max(0, note_timer - 300)  # Rewind by 5 seconds (assuming 60 FPS)
    note_index = 0
    for i, note in enumerate(note_instructions):
        if note['time'] * 60 > note_timer:
            note_index = i
            break

def main():
    global state, notes, line_y, line_direction, line_speed, note_timer, note_index
    clock = pygame.time.Clock()
    note_timer = 0
    note_index = 0

    while True:
        if state == GAME:
            line_y += line_speed * line_direction
            if line_y <= top_line_y or line_y >= bottom_line_y:
                line_direction *= -1
                line_y = max(min(line_y, bottom_line_y), top_line_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if state == MENU:
                    if event.key == pygame.K_RETURN:
                        state = GAME
                        notes = []
                elif state == GAME:
                    if event.key == pygame.K_SPACE:
                        pause_game()
                    elif event.key == pygame.K_r:
                        restart_game()
                    elif event.key == pygame.K_w:
                        rewind_game()
                elif state == PAUSE:
                    if event.key == pygame.K_SPACE:
                        state = GAME

        if state == MENU:
            screen.fill(BLACK)
            title_text = font.render("Preview", True, WHITE)
            play_text = small_font.render("Press ENTER to Preview Notes", True, WHITE)
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - title_text.get_height() // 2 - 50))
            screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, SCREEN_HEIGHT // 2 - play_text.get_height() // 2 + 50))
        elif state == GAME:
            draw_game()
            note_timer += 1
            if note_index < len(note_instructions) and note_timer > note_instructions[note_index]['time'] * 60:
                note = note_instructions[note_index]
                if 'x' in note and 'y' in note:
                    notes.append(Note(note['x'], note['y'], note.get('note_expand_speed', NOTE_EXPAND_SPEED)))
                if 'line_speed' in note:
                    line_speed = note['line_speed']
                note_index += 1
        elif state == PAUSE:
            pause_text = font.render("Paused", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()