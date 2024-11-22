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
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font("./glyphs/good_timing.otf", 64)
small_font = pygame.font.Font("./glyphs/good_timing.otf", 24)

# Game states
MENU = "menu"
GAME = "game"
state = MENU

# Notes
NOTE_RADIUS = 45
NOTE_EXPAND_SPEED = 1

# Score
score = 0
combo = 0

# Bouncing line
LINE_WIDTH = 5
LINE_HEIGHT = 20
line_y = SCREEN_HEIGHT // 2
line_direction = 1

# Feedback
feedback = ""
FEEDBACK_DURATION = 30
feedback_timer = 0
feedback_scale = 1.0
feedback_x = SCREEN_WIDTH // 2
feedback_y = SCREEN_HEIGHT // 2

# Accuracy
total_notes = 0
hit_notes = 0

# Effects
effects = []

class Note:
    def __init__(self, x, y, expand_speed):
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

    def draw(self):
        # Anti-aliasing for higher-quality shapes
        pygame.gfxdraw.aacircle(screen, self.x, self.y, NOTE_RADIUS, WHITE)
        pygame.gfxdraw.filled_circle(screen, self.x, self.y, int(self.progress), WHITE)

class Effect:
    def __init__(self, y):
        self.y = y
        self.alpha = 255

    def update(self):
        self.alpha -= 15
        if self.alpha < 0:
            self.alpha = 0

    def draw(self):
        effect_surface = pygame.Surface((SCREEN_WIDTH, 5))
        effect_surface.set_alpha(self.alpha)
        effect_surface.fill(GRAY)
        screen.blit(effect_surface, (0, self.y))

def generate_note():
    y = random.randint(100, SCREEN_HEIGHT - 100)
    return Note(SCREEN_WIDTH, y, NOTE_EXPAND_SPEED)

notes = []

def draw_menu():
    screen.fill(BLACK)
    title_text = font.render("Pulsebound", True, WHITE)
    play_text = small_font.render("Press ENTER to Play", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - title_text.get_height() // 2 - 50))
    screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, SCREEN_HEIGHT // 2 - play_text.get_height() // 2 + 50))

def draw_game():
    global score, combo, line_y, line_direction, feedback, feedback_timer, feedback_scale, feedback_x, feedback_y, total_notes, hit_notes
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
        if note.progress <= 0 and not note.expanding:
            notes.remove(note)
            combo = 0
            feedback = "Miss"
            feedback_timer = FEEDBACK_DURATION
            feedback_scale = 1.0
            feedback_x = note.x
            feedback_y = note.y
            total_notes += 1

    for effect in effects:
        effect.update()
        effect.draw()
    effects[:] = [effect for effect in effects if effect.alpha > 0]

    score_text = small_font.render(f"Score: {int(score)}", True, WHITE)
    accuracy = (hit_notes / total_notes * 100) if total_notes > 0 else 0
    accuracy_text = small_font.render(f"Accuracy: {accuracy:.2f}%", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(combo_text, (10, 50))
    screen.blit(accuracy_text, (SCREEN_WIDTH - accuracy_text.get_width() - 10, 10))
    
    if feedback_timer > 0:
        feedback_scale = 1.0 + 0.5 * (FEEDBACK_DURATION - feedback_timer) / FEEDBACK_DURATION
        feedback_alpha = int(255 * (feedback_timer / FEEDBACK_DURATION))
        feedback_text = small_font.render(f"{feedback}! x{combo}" if combo > 1 else f"{feedback}!", True, WHITE)
        feedback_text.set_alpha(feedback_alpha)
        feedback_text = pygame.transform.scale(feedback_text, (int(feedback_text.get_width() * feedback_scale), int(feedback_text.get_height() * feedback_scale)))
        screen.blit(feedback_text, (feedback_x - feedback_text.get_width() // 2, feedback_y - feedback_text.get_height() // 2))
        feedback_timer -= 1

def check_note_hit(note):
    if abs(note.y - line_y) <= NOTE_RADIUS * 2:
        if note.progress >= NOTE_RADIUS - 10:
            return "perfect"
        elif note.progress >= NOTE_RADIUS - 20:
            return "great"
    return None

def load_notes(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data['settings'], data['notes']

settings, note_instructions = load_notes('notes.json')
note_index = 0

# Apply settings
line_speed = settings['line_speed']
top_line_y = settings['top_line_y']
bottom_line_y = settings['bottom_line_y']
NOTE_SPEED = settings['note_speed']
NOTE_EXPAND_SPEED = settings['note_expand_speed']

# Starting line position and direction
line_y = SCREEN_HEIGHT // 2
line_speed = settings['line_speed']
line_direction = 1

def update_line_position():
    global line_y, line_direction

    # Update line position
    line_y += line_speed * line_direction

    # Check for boundary collisions
    if line_y >= settings['bottom_line_y'] or line_y <= settings['top_line_y']:
        line_direction *= -1
        line_y = max(min(line_y, settings['bottom_line_y']), settings['top_line_y'])

pygame.mixer.music.load('./songs/freedom_dive.mp3')

def main():
    global state, notes, score, combo, note_index, feedback, feedback_timer, feedback_scale, feedback_x, feedback_y, total_notes, hit_notes, NOTE_EXPAND_SPEED, line_speed
    clock = pygame.time.Clock()
    note_timer = 0

    while True:
        if state == GAME:
            update_line_position()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if state == MENU:
                    if event.key == pygame.K_RETURN:
                        state = GAME
                        notes = []
                        score = 0
                        combo = 0
                        note_index = 0
                        feedback = ""
                        feedback_timer = 0
                        feedback_scale = 1.0
                        total_notes = 0
                        hit_notes = 0
                        pygame.mixer.music.play()
                elif state == GAME:
                    if event.key == pygame.K_SPACE:
                        hit = False
                        for note in notes:
                            judgement = check_note_hit(note)
                            if judgement:
                                notes.remove(note)
                                feedback = judgement.capitalize()
                                feedback_timer = FEEDBACK_DURATION
                                feedback_scale = 1.0
                                feedback_x = note.x
                                feedback_y = note.y
                                total_notes += 1
                                hit = True
                                effects.append(Effect(note.y))
                                if judgement == "perfect":
                                    combo += 1
                                    hit_notes += 1
                                    score += 4044 * hit_notes // total_notes
                                elif judgement == "great":
                                    combo = 0
                                    hit_notes += 0.9
                                    score += 3076 * hit_notes // total_notes
                                else:
                                    combo = 0
                        if not hit:
                            feedback = "Miss"
                            feedback_timer = FEEDBACK_DURATION
                            feedback_scale = 1.0
                            feedback_x = SCREEN_WIDTH // 2
                            feedback_y = line_y
                            combo = 0
                            total_notes += 1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hit = False
                for note in notes:
                    judgement = check_note_hit(note)
                    if judgement:
                        notes.remove(note)
                        feedback = judgement.capitalize()
                        feedback_timer = FEEDBACK_DURATION
                        feedback_scale = 1.0
                        feedback_x = note.x
                        feedback_y = note.y
                        total_notes += 1
                        hit = True
                        effects.append(Effect(note.y))
                        if judgement == "perfect":
                            combo += 1
                            hit_notes += 1
                            score += 4044 * hit_notes // total_notes
                        elif judgement == "great":
                            combo = 0
                            hit_notes += 0.9
                            score += 3076 * hit_notes // total_notes
                        else:
                            combo = 0
                if not hit:
                    feedback = "Miss"
                    feedback_timer = FEEDBACK_DURATION
                    feedback_scale = 1.0
                    feedback_x = SCREEN_WIDTH // 2
                    feedback_y = line_y
                    combo = 0
                    total_notes += 1

        if state == MENU:
            draw_menu()
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

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()