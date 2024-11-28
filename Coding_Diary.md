# AI Coding Diary

## Project Name: _Hackathon Rhythm Game_

### Date: _11/22/2024_

## 1. **Task/Problem Description**

Briefly describe the problem you're trying to solve or the task you're working on.

> I need to code an application, game, or program related to the given topic (music).

---

## 2. **Initial Approach/Code**

Describe the initial approach you took to solving the problem. If you started writing code, include it here.

```python
# Hide the Pygame support prompt
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame, sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rhythm Game")

FPS = 60

# Font properties and text rendering
font_path = "./glyphs/rubik_bold.ttf"
font = pygame.font.Font(font_path, 84)
small_font = pygame.font.Font(font_path, 24)

# Notes
NOTE_RADIUS = 45
note_expand_speed = 1

# Score
score = 0
combo = 0

# Accuracy
total_notes = 0
hit_notes = 0

clock = pygame.time.Clock()
note_timer = 0
while True:
    title_text = font.render("Rhythm Game", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(title_text, title_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
    clock.tick(FPS)
```

- What was your plan for solving the problem?
  - Lay the foundations for the game, then allow AI to expand on it and set up the baseline for the game.
- Did you have any initial thoughts or strategies before using AI?
  - Set up the variables and the basic layout of the game. Display the menu screen and add basic controls.

---

## 3. **Interaction with AI**

### Questions/Requests to AI

Write down the questions or requests you made to AI.
Also include what code from AI you are unsure of and craft a question that asks for further clarification.

- N/A; I understand all of the code that AI returned.

```text
- Use the `json` library to import and cache notes from `notes.json`. Store attributes like `line_speed` and `note_expand_speed` into variables so that they can be loaded into the game later on.
- Render the upper and lower boundary lines based on their y-values stored in `notes.json`. Additionally, render a gray line that bounces off the boundary lines. Every time the line bounces off a boundary line, make that boundary line flash a color (red a blue).
- Draw the notes as an outer circle that encapsulates an inner (expanding) circle. The expansion duration should be based on the `note_expand_speed` imported earlier. Make the note disappear after it has dilated to the radius of its parent circle.
- Actually, make the inner circle shrink to radius zero, then make the note disappear.
- How can I make my code more organized?
```

---

## 4. **AI's Suggestions/Code Changes**

Record the code or suggestions AI provided. Include any changes or improvements AI suggested and how it influenced your approach.

In the code below, AI actually did not draw the flashing boundary line colors correctly; however, I thought this version actually looked better, so I decided to keep it.

```python
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
            boundary_effects.append({'y': bouncing_line_y + top_line_bounce, 'alpha': 255, 'color': RED})
        else:
            bottom_line_bounce = BOUNCE_DISTANCE
            boundary_effects.append({'y': bouncing_line_y + bottom_line_bounce, 'alpha': 255, 'color': BLUE})
```

Below is the code that AI initially returned for the `note.py` module. I later added anti-aliasing to allow for higher-quality shapes.

```python
import pygame

NOTE_RADIUS = 45
WHITE = (255, 255, 255)

class Note:
    def __init__(self, x, y, expand_speed):
        self.x = x
        self.y = y
        self.progress = 0
        self.expand_speed = expand_speed
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
        # Draw outer circle
        pygame.draw.circle(screen, WHITE, (self.x, self.y), NOTE_RADIUS, 1)  # 1 is the width for an outline
        # Draw inner expanding/shrinking circle
        pygame.draw.circle(screen, WHITE, (self.x, self.y), int(self.progress))
```

- What was AI's solution or suggestion?
  - AI separated the code into different classes/modules for better organization.
- How did it differ from your original approach?
  - I originally planned to put everything into one file, but I then realized that the code would look very overwhelming and difficult to read.

---

## 5. **Reflection on Changes**

Reflect on the changes made to your code after AI's suggestions. Answer the following questions:

- Why do you think AI's suggestions are helpful or relevant?
- AI is great at code organization and generating basic mechanics for projects. Using AI to set the baseline for your project can be great, as it helps you expand on your ideas and carry them out with ease.
- Did the suggestions improve your code? How?

  - The suggestions did improve my code. As mentioned previously, my code was very messy and unorganized, and AI suggested that I organize major functions/classes into their own files so that it would be easier to read.
- Did you understand why the changes were made, or are you still uncertain about some parts?

  - Yes, I understood why the changes were made. After examining the code that AI returned, I was able to fully grasp the concepts used. I was later able to reapply the techniques on different mechanics of the game.
    - For example, I was stuck on creating the fade-in animation that was meant to be played upon pressing the `PLAY` button. It kept appearing empty, with no animation at all. AI helped me fix my code by mentioning how I needed to draw the game elements first, then draw the overlay.
      ```python
      if fade_alpha > 0:
          fade_alpha -= 5
          fade_surface.set_alpha(fade_alpha)
          line_speed = 5
          draw_game()  # Draw the game elements first
          screen.blit(fade_surface, (0, 0))  # Draw the fade surface above the game elements
      ```

---

## 6. **Testing and Results**

After making the changes, did you test your code? What were the results?

- Did you run any tests (e.g., unit tests, edge cases)?

  - I ran a few tests to see if the code worked. There were some bugs, but I was able to get them fixed quickly.
- Did the code work as expected after incorporating AI's changes?

  - The code did not work exactly as I expected. As I mentioned earlier, AI did not draw the flashing boundary line colors correctly. However, I decided to keep it anyway since it looked better then my original plan.
- Did you encounter any bugs or issues during testing?

  - The program also ran into several issues due to some missing variables. I simply fixed these by initializing the missing variables with filler values (e.g., `None` or `0`) that are changed later in the game.

---

## 7. **What Did You Learn?**

In this section, reflect on what you learned from this coding session. Did you gain any new insights, or were there areas you still struggled with?

> I learned how to properly organize my code so that it is much more readable. I also learned many new features in Pygame, such as anti-aliasing and sound output.

---
