r"""
                         ___              ___   ___
                        /HH/             /GI/   \MM\        
                       /EE/             /VE/     \UU\       
                      /LL/             /ME/       \CC\      
                     /OO/             /A1/         \HH\     
                    /WW/             /00/           \TT\    
                    \OO\            /%P/            /HH/    
                     \RR\          /LE/            /AA/     
                      \LL\        /AS/            /NN/      
                       \DD\      /E!/            /KK/       
                        \!!\    /!!/            /SS/        
                         ‾‾‾    ‾‾‾             ‾‾‾
"""

# Hide the Pygame support prompt
from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame, sys, random, os
from mutagen.mp3 import MP3
from modules.note import Note
from modules.utils import load_player, load_notes, check_note_hit, save_player
from modules.button import Button

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pulsebound: Celestial Drift")
pygame.display.set_icon(pygame.image.load("./images/icon.png"))

# Set the FPS of the game
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (225, 187, 37)
INDIGO = (80, 44, 180)
RED = (241, 125, 126)
BLUE = (147, 93, 233)
GRAY = (200, 200, 200)

# Font properties and text rendering
font_path = "./glyphs/rubik_bold.ttf"
font = pygame.font.Font(font_path, 84)  # Title font
subtitle_font = pygame.font.Font(font_path, 36)  # Subtitle font 
small_font = pygame.font.Font(font_path, 24)  # Small font
tiny_font = pygame.font.Font(font_path, 18)  # Tiny font

# Menu song properties
menu_song = pygame.mixer.Sound("./songs/new_morning_new_sun.wav")
menu_song.set_volume(0.5)
menu_song_playing = False

# Load sound effects
click_sound = pygame.mixer.Sound("./sfx/press.wav")  # Button click SFX
start_sound = pygame.mixer.Sound("./sfx/start.wav")  # Game start SFX (game begins)
countdown_sound = pygame.mixer.Sound("./sfx/countdown.wav")  # Countdown SFX
countdown_end_sound = pygame.mixer.Sound("./sfx/countdown_end.wav")  # Game begin SFX (countdown finished)
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
note_expand_speed = 1  # Default note expansion speed

# Score
score = 0  # Player score
combo = 0  # Combo counter
PERFECT_INCREMENT = 12816  # Perfect note score increment
GOOD_INCREMENT = 6518  # Good note score increment
BAD_INCREMENT = 2478  # Bad note score increment

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
settings, note_instructions = load_notes("notes.json")
top_line_y = settings["top_line_y"]
bottom_line_y = settings["bottom_line_y"]
line_speed = settings["line_speed"]

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
        "x": random.randint(0, SCREEN_WIDTH),  # Initial x-position
        "y": random.randint(0, SCREEN_HEIGHT),  # Initial y-position
        "dx": random.uniform(-0.2, 0.2),  # Horizontal change
        "dy": random.uniform(-0.2, 0.2),  # Vertical change
        "alpha": random.randint(50, 150)  # Generate a random alpha value between 50 and 150
    }
    for _ in range(50)  # Create 50 particles (repeat the dictionary creation 50 times)
]

def update_particles() -> None:
    for particle in particles:
        particle["x"] += particle["dx"]
        particle["y"] += particle["dy"]
        if not 0 < particle["x"] < SCREEN_WIDTH:
            # Reverse the horizontal direction if the particle reaches the left or right edge of the screen
            particle["dx"] *= -1
        if not 0 < particle["y"] < SCREEN_HEIGHT:
            # Reverse the vertical direction if the particle reaches the top or bottom edge of the screen
            particle["dy"] *= -1

def draw_particles() -> None:
    for particle in particles:
        # Create a surface and blit the particle onto it (to allow for alpha options)
        particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        particle_surface.fill((255, 255, 255, particle["alpha"]))
        screen.blit(particle_surface, (int(particle["x"]), int(particle["y"])))

def draw_menu() -> None:
    screen.fill(BLACK)

    draw_particles()

    player = load_player("./player.json")

    title_text = font.render("PULSEBOUND", True, WHITE)
    subtitle_text = subtitle_font.render("CELESTIAL DRIFT", True, GRAY)
    previous_score_text = tiny_font.render(f"LAST SCORE {player['previous_score']} ({player['previous_rating']})", True, (140, 140, 140))
    previous_accuracy_text = tiny_font.render(f"LAST ACCURACY {player['previous_accuracy']:.2f}%", True, (140, 140, 140))
    best_score_text = tiny_font.render(f"BEST SCORE {player['best_score']} ({player['best_rating']})", True, (140, 140, 140))
    best_accuracy_text = tiny_font.render(f"BEST ACCURACY {player['best_accuracy']:.2f}%", True, (140, 140, 140))

    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    
    screen.blit(title_text, title_rect)
    screen.blit(subtitle_text, subtitle_rect)
    screen.blit(previous_score_text, (20, 20))
    screen.blit(previous_accuracy_text, (SCREEN_WIDTH - previous_accuracy_text.get_width() - 20, 20))
    screen.blit(best_score_text, (20, SCREEN_HEIGHT - best_score_text.get_height() - 20))
    screen.blit(best_accuracy_text, (SCREEN_WIDTH - best_accuracy_text.get_width() - 20, SCREEN_HEIGHT - best_accuracy_text.get_height() - 20))

    play_button.draw(screen)

# Boundary bounce effect
BOUNCE_DISTANCE = 20
bounce_speed = line_speed / 3
top_line_bounce = 0
bottom_line_bounce = 0

# Initial label positions
song_x = SCREEN_WIDTH

def draw_game() -> None:
    global score, combo, bouncing_line_y, line_direction, feedback, feedback_timer, feedback_scale, feedback_x, feedback_y, total_notes, hit_notes, bounce_speed, top_line_bounce, bottom_line_bounce, song_x, score_percentage, score_rating, accuracy
    
    screen.fill(BLACK)
    
    # Scrolling label for song title
    song = small_font.render("CELESTIAL DRIFT", True, (24, 24, 24))
    song_x -= 1 / FPS / song_length * (SCREEN_WIDTH + song.get_width())
    screen.blit(song, (song_x, top_line_y + 15))

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
                "y": bouncing_line_y + top_line_bounce,
                "alpha": 255,
                "color": GOLD
            }
        )
    elif bouncing_line_y >= bottom_line_y:
        line_direction *= -1
        bouncing_line_y = bottom_line_y
        bottom_line_bounce = BOUNCE_DISTANCE
        boundary_effects.append(
            {
                "y": bouncing_line_y + bottom_line_bounce,
                "alpha": 255,
                "color": INDIGO
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
            feedback = "MISS"
            feedback_timer = FEEDBACK_DURATION
            feedback_scale = 1.0
            feedback_x = note.x
            feedback_y = note.y
            total_notes += 1

    for effect in boundary_effects:
        effect["alpha"] -= line_speed
        if effect["alpha"] < 0:
            effect["alpha"] = 0
        effect_surface = pygame.Surface((SCREEN_WIDTH, 10))
        effect_surface.set_alpha(effect["alpha"])
        effect_surface.fill(effect["color"]) 
        screen.blit(effect_surface, (0, effect["y"] - 4))
    boundary_effects[:] = [effect for effect in boundary_effects if effect["alpha"] > 0]

    for effect in horizontal_effects:
        effect["alpha"] -= 15
        if effect["alpha"] < 0:
            effect["alpha"] = 0
        effect_surface = pygame.Surface((SCREEN_WIDTH, 5))
        effect_surface.set_alpha(effect["alpha"])
        effect_surface.fill(GRAY)
        screen.blit(effect_surface, (0, effect["y"]))
    horizontal_effects[:] = [effect for effect in horizontal_effects if effect["alpha"] > 0]

    for effect in vertical_effects:
        effect["alpha"] -= 15
        if effect["alpha"] < 0:
            effect["alpha"] = 0
        effect_surface = pygame.Surface((5, bottom_line_y - top_line_y))
        effect_surface.set_alpha(effect["alpha"])
        effect_surface.fill(GRAY)
        screen.blit(effect_surface, (effect["x"], top_line_y))
    vertical_effects[:] = [effect for effect in vertical_effects if effect["alpha"] > 0]

    score_percentage = score / (PERFECT_INCREMENT * max(note["id"] for note in note_instructions if "id" in note)) * 100
    score_rating = (
        "S+" if score_percentage >= 100 else
        "S" if score_percentage >= 250 / 3 else
        "A" if score_percentage >= 200 / 3 else
        "B" if score_percentage >= 50 else
        "C" if score_percentage >= 100 / 3 else
        "D" if score_percentage >= 50 / 3 else
        "F"
    )
    accuracy = (hit_notes / total_notes * 100) if total_notes > 0 else 0

    score_text = small_font.render(f"SCORE {score} ({score_rating})", True, WHITE)
    accuracy_text = small_font.render(f"ACCURACY {accuracy:.2f}%", True, WHITE)
    screen.blit(score_text, (20, 20))
    screen.blit(accuracy_text, (SCREEN_WIDTH - accuracy_text.get_width() - 20, 20))
    
    if feedback_timer > 0:
        feedback_scale = 1.0 + 0.5 * (FEEDBACK_DURATION - feedback_timer) / FEEDBACK_DURATION
        feedback_alpha = int(255 * (feedback_timer / FEEDBACK_DURATION))
        feedback_text = small_font.render(
            f"{feedback}! x{combo}" if combo > 1 else f"{feedback}!",
            True,
            RED if feedback == "MISS" else BLUE if feedback == "PERFECT" else GRAY
        )
        feedback_text.set_alpha(feedback_alpha)
        feedback_text = pygame.transform.scale(feedback_text, (int(feedback_text.get_width() * feedback_scale), int(feedback_text.get_height() * feedback_scale)))
        screen.blit(feedback_text, (feedback_x - feedback_text.get_width() // 2, feedback_y - feedback_text.get_height() // 2))

        feedback_timer -= 1

def update_line_position() -> None:
    global bouncing_line_y, line_direction, top_line_bounce, bottom_line_bounce

    # Update line position
    bouncing_line_y += line_speed * line_direction

    # Check for boundary collisions
    if bouncing_line_y >= settings["bottom_line_y"] or bouncing_line_y <= settings["top_line_y"]:
        line_direction *= -1
        bouncing_line_y = max(min(bouncing_line_y, settings["bottom_line_y"]), settings["top_line_y"])
        if bouncing_line_y == settings["top_line_y"]:
            top_line_bounce = -BOUNCE_DISTANCE
            boundary_effects.append(
                {
                    "y": bouncing_line_y + top_line_bounce,
                    "alpha": 255,
                    "color": GOLD
                }
            )
        else:
            bottom_line_bounce = BOUNCE_DISTANCE
            boundary_effects.append(
                {
                    "y": bouncing_line_y + bottom_line_bounce,
                    "alpha": 255,
                    "color": INDIGO
                }
            )

pygame.mixer.music.load("./songs/celestial_drift.mp3")
song = MP3("./songs/celestial_drift.mp3")
song_length = song.info.length

def save_player_data() -> None:
    player = load_player("./player.json")
    player["previous_score"] = score
    player["previous_rating"] = score_rating
    player["previous_accuracy"] = round(accuracy, 2)
    if player["previous_score"] > player["best_score"]:
        player["best_score"] = player["previous_score"]
        player["best_rating"] = player["previous_rating"]
    if round(player["previous_accuracy"], 2) > player["best_accuracy"]:
        player["best_accuracy"] = round(player["previous_accuracy"], 2)
    save_player("./player.json", player)

def restart_program() -> None:
    os.execv(sys.executable, ["python", "main.py"])

# Initialize note timer
note_timer = 0

def main():
    global state, notes, score, combo, note_index, feedback, feedback_timer, feedback_scale, feedback_x, feedback_y, total_notes, hit_notes, note_expand_speed, line_speed, menu_song_playing, fade_alpha, countdown_began, countdown_timer, previous_countdown, countdown, note_timer

    clock = pygame.time.Clock()
    # Remove note_timer variable
    # note_timer = 0

    # Set initial line speed from settings
    line_speed = settings["line_speed"]

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
                elif state == GAME:
                    if event.key == pygame.K_ESCAPE:
                        state = GAME_COMPLETE_FADE_OUT
                        pygame.mixer.music.stop()
                    else:
                        hit = False
                        for note in notes:
                            judgment = check_note_hit(note, bouncing_line_y, line_speed)
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
                                        "y": note.y,
                                        "alpha": 255
                                    }
                                )
                                vertical_effects.append(
                                    {
                                        "x": note.x,
                                        "alpha": 255
                                    }
                                )
                                if judgment == "perfect":
                                    combo += 1
                                    hit_notes += 1
                                    score += int(PERFECT_INCREMENT * hit_notes / total_notes)
                                elif judgment == "good":
                                    combo = 0
                                    hit_notes += 0.9
                                    score += int(GOOD_INCREMENT * hit_notes / total_notes)
                                elif judgment == "bad":
                                    combo = 0
                                    hit_notes += 0.65
                                    score += int(BAD_INCREMENT * hit_notes / total_notes)
                                else:
                                    combo = 0
                            if not hit:
                                feedback = "MISS"
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
                        judgment = check_note_hit(note, bouncing_line_y, line_speed)
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
                                    "y": note.y,
                                    "alpha": 255
                                }
                            )
                            vertical_effects.append(
                                {
                                    "x": note.x,
                                    "alpha": 255
                                }
                            )
                            if judgment == "perfect":
                                combo += 1
                                hit_notes += 1
                                score += int(PERFECT_INCREMENT * hit_notes / total_notes)
                            elif judgment == "good":
                                combo = 0
                                hit_notes += 0.9
                                score += int(GOOD_INCREMENT * hit_notes / total_notes)
                            elif judgment == "bad":
                                combo = 0
                                hit_notes += 0.65
                                score += int(BAD_INCREMENT * hit_notes / total_notes)
                            else:
                                combo = 0
                    if not hit:
                        feedback = "MISS"
                        feedback_timer = FEEDBACK_DURATION
                        feedback_scale = 1.0
                        feedback_x = SCREEN_WIDTH // 2
                        feedback_y = bouncing_line_y
                        combo = 0
                        total_notes += 1
            if event.type == pygame.MOUSEBUTTONUP:
                if state == MENU:
                    # If the play button is in the "clicked" state, meaning that the source of the click is the button, and the mouse button has just been released, then switch to the "GAME" state.
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
                note_timer += 1 / FPS
                if note_index < len(note_instructions) and note_timer >= note_instructions[note_index]["time"]:
                    note = note_instructions[note_index]
                    if "x" in note and "y" in note:
                        notes.append(Note(note["x"], note["y"], note.get("note_expand_speed", note_expand_speed), line_direction))
                    if "line_speed" in note:
                        line_speed = note["line_speed"]
                    note_index += 1
                if not pygame.mixer.music.get_busy():
                    save_player_data()
                    state = GAME_COMPLETE_FADE_OUT

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()