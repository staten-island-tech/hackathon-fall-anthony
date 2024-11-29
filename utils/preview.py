import pygame, pygame.gfxdraw, sys, random, json

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pulsebound: Preview & Edit")

FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 84)
small_font = pygame.font.Font(None, 36)

# Game states
MENU = "menu"
GAME = "game"
PAUSE = "pause"
RESTART = "restart"
state = MENU

# Load settings and notes from notes.json
def load_notes(filename) -> tuple:
    with open(filename, "r") as file:
        data = json.load(file)
    return data["settings"], data["notes"]

settings, note_instructions = load_notes("notes.json")

# Apply settings
line_speed = settings["line_speed"]
top_line_y = settings["top_line_y"]
bottom_line_y = settings["bottom_line_y"]
note_expand_speed = 1.5

# Starting line position and direction
line_y = SCREEN_HEIGHT // 2
line_direction = 1

# Define LINE_WIDTH
LINE_WIDTH = 5
NOTE_RADIUS = 45

class Note:
    def __init__(self, x, y, expand_speed):
        self.x = round(x, 2)
        self.y = round(y, 2)
        self.progress = 0
        self.expand_speed = round(expand_speed, 2)
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
            self.opacity = max(0, self.opacity - ((self.expand_speed / NOTE_RADIUS) * 255))
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

# Initialize note timer
note_timer = 0

def draw_game():
    global line_y, line_direction, line_speed, note_timer, playing
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

    # Display note information
    time_text = small_font.render(f"Time: {note_timer:.3f}", True, WHITE)
    note_text = small_font.render(f"Note: {note_index}/{len(note_instructions)}", True, WHITE)
    screen.blit(time_text, (10, 10))
    screen.blit(note_text, (SCREEN_WIDTH - note_text.get_width() - 10, 10))

def pause_game():
    global state, playing
    state = PAUSE
    pygame.mixer.music.pause()
    playing = False  # Stop updating current_time when paused

def restart_game():
    global state, notes, line_y, line_direction, line_speed, note_timer, note_index, playing
    state = GAME
    notes = []
    line_y = SCREEN_HEIGHT // 2
    line_direction = 1
    line_speed = settings["line_speed"]
    note_timer = 0
    note_index = 0
    pygame.mixer.music.play()
    playing = True

def add_note():
    global line_y, note_timer
    current_time = round(note_timer, 2)
    expand_speed = round(random.uniform(0.6, 1.4), 4)
    new_note = {
        "time": round(current_time - ((NOTE_RADIUS / expand_speed) / FPS), 3),
        "x": random.randint(0, SCREEN_WIDTH),
        "y": round(line_y),
        "note_expand_speed": expand_speed
    }
    note_instructions.append(new_note)
    with open("notes.json", "w") as file:
        json.dump({"settings": settings, "notes": note_instructions}, file, indent=4)

def delete_note():
    global note_index, note_instructions
    if note_instructions:
        # Remove the selected note
        del note_instructions[note_index]
        
        # If there are still notes, ensure the note_index doesn"t exceed the length
        if note_index >= len(note_instructions):
            note_index = len(note_instructions) - 1 if len(note_instructions) > 0 else 0
        
        # Save the updated notes back to the file
        with open("notes.json", "w") as file:
            json.dump({"settings": settings, "notes": note_instructions}, file, indent=4)

def main():
    global state, notes, line_y, line_direction, line_speed, note_timer, note_index, save_index, playing
    clock = pygame.time.Clock()
    note_timer = 0
    playing = False  # This will track whether music is currently playing
    note_index = 0
    save_index = 0

    pygame.mixer.music.load("./songs/celestial_drift.mp3")

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
            elif event.type == pygame.KEYDOWN:
                if state == MENU:
                    if event.key == pygame.K_RETURN:
                        state = GAME
                        notes = []
                        pygame.mixer.music.play()
                        playing = True
                elif state == GAME:
                    if event.key == pygame.K_TAB:
                        pause_game()
                    elif event.key == pygame.K_r:
                        restart_game()
                    elif event.key == pygame.K_d:  # Press "D" to delete the current note
                        delete_note()  # Call delete_note function
                    else:
                        add_note()
                elif state == PAUSE:
                    if event.key == pygame.K_TAB:
                        state = GAME
                        pygame.mixer.music.unpause()
                        playing = True

        if state == MENU:
            screen.fill(BLACK)
            title_text = font.render("Preview", True, WHITE)
            play_text = small_font.render("Press ENTER to Preview Notes", True, WHITE)
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - title_text.get_height() // 2 - 50))
            screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, SCREEN_HEIGHT // 2 - play_text.get_height() // 2 + 50))
        elif state == GAME:
            draw_game()
            note_timer += 1 / FPS
            if note_index < len(note_instructions) and note_timer >= note_instructions[note_index]["time"]:
                note = note_instructions[note_index]
                if "x" in note and "y" in note:
                    notes.append(Note(note["x"], note["y"], note.get("note_expand_speed", note_expand_speed)))
                if "line_speed" in note:
                    line_speed = note["line_speed"]
                note_index += 1
        elif state == PAUSE:
            pause_text = font.render("Paused", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()