[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=17261170)

# Hackathon Project: Rhythm Game

### Project Title >> Pulsebound: Celestial Drift

* **Songs Used:** [New Morning, New Sun](./songs/new_morning_new_sun.wav); [Celestial Drift](./songs/celestial_drift.mp3)
    * New Morning, New Sun is the menu music. (Not AI-generated.)
    * Celestial Drift (the game music) is an AI-generated song by [Suno](https://suno.com). :)
        * Suno makes any other AI music generator a literal joke. That's how powerful it is.
        * Also, it's free (with a daily limit of ten generations).
* **Tools Used for Assistance:** ChatGPT, Phind, GitHub Copilot
* **Libaries Used:** `pygame`, `os`, `sys`, `random`, `mutagen`, `json`
* **Time Spent in Editor:** ~49 hours
    * ~70% of these hours were spent making the notes. If I'd realized earlier why the notes kept getting awfully messed up, this number would've been less than thirty.
        * Not even AI was able to fix it. The issue was that I was tracking the time using `pygame.mixer.music.get_pos()` in the note editor (`preview.py`) instead of using a frame counter variable.
            * I'm too tired to even be disappointed right now.