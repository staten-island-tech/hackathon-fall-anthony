# Hide the Pygame support prompt
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame, pygame.gfxdraw, sys, random, os
from mutagen.mp3 import MP3  # For reading MP3 file metadata
from modules.note import Note
from modules.utils import load_player, load_notes, check_note_hit, save_player  # Import save_player function

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pulsebound: Freedom Dive")
pygame.display.set_icon(pygame.image.load("./images/icon.png"))

# Set the FPS of the game
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (248, 84, 84)
BLUE = (66, 148, 248)
GRAY = (200, 200, 200)

# Font properties and text rendering
font_path = "./glyphs/rubik_bold.ttf"
font = pygame.font.Font(font_path, 84)  # Title font
subtitle_font = pygame.font.Font(font_path, 36)  # Subtitle font 
small_font = pygame.font.Font(font_path, 24)  # Small font
tiny_font = pygame.font.Font(font_path, 18)  # Tiny font

# Menu song properties
menu_song = pygame.mixer.Sound('./songs/new_morning_new_sun.wav')
menu_song.set_volume(0.5)
menu_song_playing = False

# Load sound effects
click_sound = pygame.mixer.Sound('./sfx/press.wav')  # Button click SFX
start_sound = pygame.mixer.Sound('./sfx/start.wav')  # Game start SFX (game begins)
countdown_sound = pygame.mixer.Sound('./sfx/countdown.wav')  # Countdown SFX
countdown_end_sound = pygame.mixer.Sound('./sfx/countdown_end.wav')  # Game begin SFX (countdown finished)
countdown_sound.set_volume(0.5)
countdown_end_sound.set_volume(0.5)

# Game states (constants)
MENU = "menu"
GAME = "game"
FADE_OUT = "fade_out"
FADE_IN = "fade_in"
GAME_COMPLETE_FADE_OUT = "fade_out_from_game"
GAME_COMPLETE_FADE_IN = "fade_in_from_game"
state = MENU  # Menu state by default

# Notes
NOTE_RADIUS = 45  # Note radius (constant)
note_expand_speed = 1  # Default note expansion speed (1)

# Score
score = 0  # Player score
combo = 0  # Combo counter

# Bouncing line
LINE_WIDTH = 5
LINE_HEIGHT = 20
bouncing_line_y = SCREEN_HEIGHT // 2
line_direction = 1

# Feedback
feedback = ""  # Feedback message (PERFECT, GOOD, or MISS) is set to an empty string by default
FEEDBACK_DURATION = 30  # Feedback duration (frames)
feedback_timer = 0  # When this reaches FEEDBACK_DURATION, feedback message disappears
feedback_scale = 1.0  # Original feedback message scale (1.0)
feedback_x = SCREEN_WIDTH // 2  # Feedback message x-position
feedback_y = SCREEN_HEIGHT // 2  # Feedback message y-position

# Accuracy
total_notes = 0
hit_notes = 0

# Effects
effects = []  # Note hit effect
boundary_effects = []  # Boundary bounce effect
horizontal_effects = [] # Horizontal line display (for note hits)
vertical_effects = []  # Vertical line display (for note hits)

# Cache the notes and settings from notes.json
notes = []
settings, note_instructions = load_notes('notes.json')
top_line_y = settings['top_line_y']
bottom_line_y = settings['bottom_line_y']
line_speed = settings['line_speed']

class Button:
    'Button class for creating buttons (clickable images)'

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

play_button = Button(
    (SCREEN_WIDTH // 2 - 77, SCREEN_HEIGHT // 2 + 60),  # Position of default button image
    (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 57),  # Position of pressed button image
    (154, 74),  # Dimensions of default button image
    (160, 80),  # Dimensions of pressed button image
    "./images/buttons/play/default.png",  # Default button image
    "./images/buttons/play/pressed.png"  # Pressed button image
)

# Background particles
particles = [
    {
        'x': random.randint(0, SCREEN_WIDTH),  # Initial x-position
        'y': random.randint(0, SCREEN_HEIGHT),  # Initial y-position
        'dx': random.uniform(-0.2, 0.2),  # Horizontal change
        'dy': random.uniform(-0.2, 0.2),  # Vertical change
        'alpha': random.randint(50, 150)  # Generate a random alpha value between 50 and 150
    }
    for _ in range(50)  # Create 50 particles (repeat the dictionary creation 50 times)
]

def update_particles():
    for particle in particles:
        particle['x'] += particle['dx']
        particle['y'] += particle['dy']
        if not 0 < particle['x'] < SCREEN_WIDTH:
            # Reverse the horizontal direction if the particle reaches the left or right edge of the screen
            particle['dx'] *= -1
        if not 0 < particle['y'] < SCREEN_HEIGHT:
            # Reverse the vertical direction if the particle reaches the top or bottom edge of the screen
            particle['dy'] *= -1

def draw_particles():
    for particle in particles:
        # Create a surface and blit the particle onto it (to allow for alpha options)
        particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        particle_surface.fill((255, 255, 255, particle['alpha']))
        screen.blit(particle_surface, (int(particle['x']), int(particle['y'])))

def draw_menu():
    screen.fill(BLACK)

    draw_particles()

    player = load_player("./player.json")

    title_text = font.render("PULSEBOUND", True, WHITE)
    subtitle_text = subtitle_font.render("FREEDOM DIVE", True, GRAY)
    previous_score_text = tiny_font.render(f"LAST SCORE {player['previous_score']}", True, (140, 140, 140))
    previous_accuracy_text = tiny_font.render(f"LAST ACCURACY {player['previous_accuracy']:.2f}%", True, (140, 140, 140))
    best_score_text = tiny_font.render(f"BEST SCORE {player['best_score']}", True, (140, 140, 140))
    best_accuracy_text = tiny_font.render(f"BEST ACCURACY {player['best_accuracy']:.2f}%", True, (140, 140, 140))

    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    
    screen.blit(title_text, title_rect)
    screen.blit(subtitle_text, subtitle_rect)
    screen.blit(previous_score_text, (20, 20))
    screen.blit(previous_accuracy_text, (SCREEN_WIDTH - previous_accuracy_text.get_width() - 20, 20))
    screen.blit(best_score_text, (20, SCREEN_HEIGHT - best_score_text.get_height() - 20))
    screen.blit(best_accuracy_text, (SCREEN_WIDTH - previous_accuracy_text.get_width() - 20, SCREEN_HEIGHT - best_accuracy_text.get_height() - 20))

    play_button.draw(screen)

# Boundary bounce effect
BOUNCE_DISTANCE = 20
bounce_speed = line_speed / 3
top_line_bounce = 0
bottom_line_bounce = 0

# Label (for song) position
label_x = SCREEN_WIDTH

def draw_game():
    global score, combo, bouncing_line_y, line_direction, feedback, feedback_timer, feedback_scale, feedback_x, feedback_y, total_notes, hit_notes, bounce_speed, top_line_bounce, bottom_line_bounce, label_x
    screen.fill(BLACK)
    
    # Scrolling label for song title
    label = small_font.render("XI - FREEDOM DIVE", True, (24, 24, 24))
    label_x -= 1 / FPS / song_length * (SCREEN_WIDTH + label.get_width())
    screen.blit(label, (label_x, top_line_y + 15))

    draw_particles()  # Draw the particles on the screen

    # Draw the main game elements/lines
    pygame.draw.line(
        screen,
        WHITE,
        (0, top_line_y + top_line_bounce),
        (SCREEN_WIDTH, top_line_y + top_line_bounce),
        10
    )
    pygame.draw.line(
        screen,
        WHITE,
        (0, bottom_line_y + bottom_line_bounce),
        (SCREEN_WIDTH, bottom_line_y + bottom_line_bounce),
        10
    )
    pygame.draw.line(
        screen,
        GRAY,
        (0, bouncing_line_y),
        (SCREEN_WIDTH, bouncing_line_y),
        LINE_WIDTH
    )
    
    bouncing_line_y += line_speed * line_direction
    if bouncing_line_y <= top_line_y:
        line_direction *= -1
        bouncing_line_y = top_line_y
        top_line_bounce = -BOUNCE_DISTANCE
        boundary_effects.append(
            {
                'y': bouncing_line_y + top_line_bounce,
                'alpha': 255,
                'color': RED
            }
        )
    elif bouncing_line_y >= bottom_line_y:
        line_direction *= -1
        bouncing_line_y = bottom_line_y
        bottom_line_bounce = BOUNCE_DISTANCE
        boundary_effects.append(
            {
                'y': bouncing_line_y + bottom_line_bounce,
                'alpha': 255,
                'color': BLUE
            }
        )

    bounce_speed = line_speed / 3

    if top_line_bounce < 0:
        top_line_bounce += bounce_speed
    if bottom_line_bounce > 0:
        bottom_line_bounce -= bounce_speed

    for note in notes:
        note.expand()
        note.draw(screen)
        if note.progress <= 0 and not note.expanding:
            notes.remove(note)
            combo = 0
            feedback = "Miss"
            feedback_timer = FEEDBACK_DURATION
            feedback_scale = 1.0
            feedback_x = note.x
            feedback_y = note.y
            total_notes += 1

    for effect in boundary_effects:
        effect['alpha'] -= line_speed
        if effect['alpha'] < 0:
            effect['alpha'] = 0
        effect_surface = pygame.Surface((SCREEN_WIDTH, 10))
        effect_surface.set_alpha(effect['alpha'])
        effect_surface.fill(effect['color']) 
        screen.blit(effect_surface, (0, effect['y'] - 4))
    boundary_effects[:] = [effect for effect in boundary_effects if effect['alpha'] > 0]

    for effect in horizontal_effects:
        effect['alpha'] -= 15
        if effect['alpha'] < 0:
            effect['alpha'] = 0
        effect_surface = pygame.Surface((SCREEN_WIDTH, 5))
        effect_surface.set_alpha(effect['alpha'])
        effect_surface.fill(GRAY)
        screen.blit(effect_surface, (0, effect['y']))
    horizontal_effects[:] = [effect for effect in horizontal_effects if effect['alpha'] > 0]

    for effect in vertical_effects:
        effect['alpha'] -= 15
        if effect['alpha'] < 0:
            effect['alpha'] = 0
        effect_surface = pygame.Surface((5, bottom_line_y - top_line_y))
        effect_surface.set_alpha(effect['alpha'])
        effect_surface.fill(GRAY)
        screen.blit(effect_surface, (effect['x'], top_line_y))
    vertical_effects[:] = [effect for effect in vertical_effects if effect['alpha'] > 0]

    score_text = small_font.render(f"SCORE {int(score)}", True, WHITE)
    accuracy = (hit_notes / total_notes * 100) if total_notes > 0 else 0
    accuracy_text = small_font.render(f"ACCURACY {accuracy:.2f}%", True, WHITE)
    screen.blit(score_text, (20, 20))
    screen.blit(accuracy_text, (SCREEN_WIDTH - accuracy_text.get_width() - 20, 20))
    
    if feedback_timer > 0:
        feedback_scale = 1.0 + 0.5 * (FEEDBACK_DURATION - feedback_timer) / FEEDBACK_DURATION
        feedback_alpha = int(255 * (feedback_timer / FEEDBACK_DURATION))
        feedback_text = small_font.render(
            f"{feedback}! x{combo}" if combo > 1 else f"{feedback}!",
            True,
            GRAY
        )
        feedback_text.set_alpha(feedback_alpha)
        feedback_text = pygame.transform.scale(feedback_text, (int(feedback_text.get_width() * feedback_scale), int(feedback_text.get_height() * feedback_scale)))
        screen.blit(feedback_text, (feedback_x - feedback_text.get_width() // 2, feedback_y - feedback_text.get_height() // 2))
        feedback_timer -= 1

def update_line_position():
    global bouncing_line_y, line_direction, top_line_bounce, bottom_line_bounce

    # Update line position
    bouncing_line_y += line_speed * line_direction

    # Check for boundary collisions
    if bouncing_line_y >= settings['bottom_line_y'] or bouncing_line_y <= settings['top_line_y']:
        line_direction *= -1
        bouncing_line_y = max(min(bouncing_line_y, settings['bottom_line_y']), settings['top_line_y'])
        if bouncing_line_y == settings['top_line_y']:
            top_line_bounce = -BOUNCE_DISTANCE
            boundary_effects.append(
                {
                    'y': bouncing_line_y + top_line_bounce,
                    'alpha': 255,
                    'color': RED
                }
            )
        else:
            bottom_line_bounce = BOUNCE_DISTANCE
            boundary_effects.append(
                {
                    'y': bouncing_line_y + bottom_line_bounce,
                    'alpha': 255,
                    'color': BLUE
                }
            )

pygame.mixer.music.load('./songs/freedom_dive.mp3')
pygame.mixer.music.set_volume(0.4)
song = MP3('./songs/freedom_dive.mp3')
song_length = song.info.length

def save_player_data():
    global score, total_notes, hit_notes
    
    accuracy = (hit_notes / total_notes * 100) if total_notes > 0 else 0
    player = load_player("./player.json")
    player["previous_score"] = int(score)
    player["previous_accuracy"] = round(accuracy, 2)
    if int(score) > player["best_score"]:
        player["best_score"] = int(score)
    if round(accuracy, 2) > player["best_accuracy"]:
        player["best_accuracy"] = round(accuracy, 2)
    save_player("./player.json", player)

def restart_program():
    os.execl(sys.executable, sys.executable, *sys.argv)

def main():
    global state, notes, score, combo, note_index, feedback, feedback_timer, feedback_scale, feedback_x, feedback_y, total_notes, hit_notes, note_expand_speed, line_speed, menu_song_playing, fade_alpha, countdown_began, countdown_timer, previous_countdown, countdown

    clock = pygame.time.Clock()
    note_timer = 0

    # Set initial line speed from settings
    line_speed = settings['line_speed']

    # Initialize the fade surface and its properties
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    fade_surface.fill(BLACK)
    fade_alpha = 0

    # Game countdown
    countdown_began = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if state == MENU:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = FADE_OUT
                        start_sound.play()
                if state == GAME:
                    if event.key == pygame.K_ESCAPE:
                        state = GAME_COMPLETE_FADE_OUT
                        pygame.mixer.music.stop()
                    if event.key == pygame.K_SPACE:
                        hit = False
                        for note in notes:
                            judgment = check_note_hit(note, bouncing_line_y)
                            if judgment:
                                notes.remove(note)
                                feedback = judgment.upper()
                                feedback_timer = FEEDBACK_DURATION
                                feedback_scale = 1.0
                                feedback_x = note.x
                                feedback_y = note.y
                                total_notes += 1
                                hit = True
                                horizontal_effects.append(
                                    {
                                        'y': note.y,
                                        'alpha': 255
                                    }
                                )
                                vertical_effects.append(
                                    {
                                        'x': note.x,
                                        'alpha': 255
                                    }
                                )
                                if judgment == "perfect":
                                    combo += 1
                                    hit_notes += 1
                                    score += 4044 * hit_notes // total_notes
                                elif judgment == "good":
                                    combo = 0
                                    hit_notes += 0.9
                                    score += 3076 * hit_notes // total_notes
                                elif judgment == "bad":
                                    combo = 0
                                    hit_notes += 0.65
                                    score += 1204 * hit_notes // total_notes
                                else:
                                    combo = 0
                        if not hit:
                            feedback = "Miss"
                            feedback_timer = FEEDBACK_DURATION
                            feedback_scale = 1.0
                            feedback_x = SCREEN_WIDTH // 2
                            feedback_y = bouncing_line_y
                            combo = 0
                            total_notes += 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == MENU:
                    if play_button.is_clicked(event.pos):
                        play_button.clicked = True
                        click_sound.play()
                elif state == GAME:
                    hit = False
                    for note in notes:
                        judgment = check_note_hit(note, bouncing_line_y)
                        if judgment:
                            notes.remove(note)
                            feedback = judgment.capitalize()
                            feedback_timer = FEEDBACK_DURATION
                            feedback_scale = 1.0
                            feedback_x = note.x
                            feedback_y = note.y
                            total_notes += 1
                            hit = True
                            horizontal_effects.append(
                                {
                                    'y': note.y,
                                    'alpha': 255
                                }
                            )
                            vertical_effects.append(
                                {
                                    'x': note.x,
                                    'alpha': 255
                                }
                            )
                            if judgment == "perfect":
                                combo += 1
                                hit_notes += 1
                                score += 4044 * hit_notes // total_notes
                            elif judgment == "good":
                                combo = 0
                                hit_notes += 0.9
                                score += 3076 * hit_notes // total_notes
                            elif judgment == "bad":
                                combo = 0
                                hit_notes += 0.6
                                score += 1204 * hit_notes // total_notes
                            else:
                                combo = 0
                    if not hit:
                        feedback = "Miss"
                        feedback_timer = FEEDBACK_DURATION
                        feedback_scale = 1.0
                        feedback_x = SCREEN_WIDTH // 2
                        feedback_y = bouncing_line_y
                        combo = 0
                        total_notes += 1
            if event.type == pygame.MOUSEBUTTONUP:
                if state == MENU:
                    if play_button.clicked and play_button.is_clicked(event.pos):
                        state = FADE_OUT
                        start_sound.play()
                    play_button.clicked = False

        if state == FADE_OUT:
            if menu_song_playing:
                menu_song.stop()
                menu_song_playing = False
            
            if fade_alpha < 255:
                fade_alpha += 5
                fade_surface.set_alpha(fade_alpha)
                draw_menu()
                screen.blit(fade_surface, (0, 0))
            else:
                fade_alpha = 255
                state = FADE_IN
        elif state == FADE_IN:
            if fade_alpha > 0:
                fade_alpha -= 5
                fade_surface.set_alpha(fade_alpha)
                line_speed = 5
                draw_game()
                screen.blit(fade_surface, (0, 0))
            else:
                fade_alpha = 0
                draw_game()
                if not countdown_began:
                    countdown_began = True
                    countdown = 3
                    middle = SCREEN_HEIGHT // 2
                    countdown_distance = abs(bouncing_line_y - middle) + ((bottom_line_y - top_line_y) if line_direction == -1 else 0)
                    countdown_timer = countdown_distance
                    previous_countdown = countdown + 1
                countdown_timer -= line_speed
                countdown = int(countdown_timer / countdown_distance * 4) if int(countdown_timer / countdown_distance * 4) > 0 else "GO!"
                if previous_countdown != countdown:
                    if countdown == "GO!":
                        countdown_end_sound.play()
                    else:
                        countdown_sound.play()
                previous_countdown = countdown
                countdown_text = font.render(str(countdown), True, WHITE)
                screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, (bottom_line_y + top_line_y) // 2 - countdown_text.get_height() // 2))
                if bouncing_line_y == SCREEN_HEIGHT // 2 and line_direction == 1:
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
        elif state == GAME_COMPLETE_FADE_OUT:
            if fade_alpha < 255:
                fade_alpha += 5
                fade_surface.set_alpha(fade_alpha)
                draw_game()
                screen.blit(fade_surface, (0, 0))
            else:
                fade_alpha = 255
                state = GAME_COMPLETE_FADE_IN
        elif state == GAME_COMPLETE_FADE_IN:
            if fade_alpha > 0:
                fade_alpha -= 5
                fade_surface.set_alpha(fade_alpha)
                draw_menu()
                screen.blit(fade_surface, (0, 0))
            else:
                fade_alpha = 0
                restart_program()
        else:
            update_particles()
            if state == MENU:
                if not menu_song_playing:
                    menu_song.play(loops=-1, fade_ms=20000)
                    menu_song_playing = True
                draw_menu()
            elif state == GAME:
                update_line_position()
                draw_game()
                note_timer += 1
                if note_index < len(note_instructions) and note_timer > note_instructions[note_index]['time'] * FPS:
                    note = note_instructions[note_index]
                    if 'x' in note and 'y' in note:
                        notes.append(Note(note['x'], note['y'], note.get('note_expand_speed', note_expand_speed)))
                    if 'line_speed' in note:
                        line_speed = note['line_speed']
                    note_index += 1
                if not pygame.mixer.music.get_busy():
                    save_player_data()
                    state = GAME_COMPLETE_FADE_OUT

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()