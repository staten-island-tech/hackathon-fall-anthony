# Game Instructions

Below are instructions guiding you on various dimensions of the game, including its installation process, its controls, and how to play it.

## Installation

To install the game and its necessary libraries, run `python3.exe -m pip install -r requirements.txt` in your dedicated terminal. Then, run `main.py` to start the game. **Make sure you are running Python version 3.11 or higher.**

## Controls

To **hit a note**, you can press any key on your keyboard (with the exception of `ESC`, as it is the key used to **exit the ongoing game**). You can use your mouse buttons to perform this action as well.

## How to Play

There are **three lines** in this game: **the upper and lower boundary lines**, as well as **the bouncing line**. The bouncing line moves **up and down between the boundary lines**. However the speed of the bouncing line can **vary** at any time.

*A common mistake is catching the note exactly when the bouncing line collides with a note. However, another factor to consider when playing the game is the expanding inner circle within each note. The inner circle expands until it has reached the radius of the outer circle, and then it shrinks until it has fully dissipated. The player must catch the note when the bouncing line hits the note and the inner circle has fully expanded.*

The accuracy is determined by the player's **precision** in hitting the notes. A maximum score of **1,255,968** can be achieved if all notes are hit perfectly. The number of consecutive perfect hits is also displayed as your **combo**.

There are **four types of judgments** that can be made when hitting a note:

- **Perfect:** The note was caught at the perfect time. (MAX. 12,816 PTS.)
- **Good:** The note was caught at a good time. (MAX. 6,518 PTS.)
- **Bad:** The note was caught at a bad time. (MAX. 2,478 PTS.)
- **Miss:** The note was missed. (0 PTS.)

Your **score increment** for each note hit also depends on your **accuracy**. The higher your accuracy, the more points you will receive for each note caught (except for misses).

*Any rating S and above is excellent. S+ is almost unobtainable, as it requires every note to be caught perfectly. If you can reach it, then you are a true rhythm master!*

Good luck; have fun! ☺
