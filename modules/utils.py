import json, os

NOTE_RADIUS = 45

def create_player(filename) -> None:
    with open(filename, 'w') as file:
        json.dump(
            {
                "previous_score": 0,
                "previous_accuracy": 0,
                "best_score": 0,
                "best_accuracy": 0.
            },
            file,
            indent=4
        )

def load_player(filename) -> dict:
    if not os.path.exists(filename):
        create_player(filename)
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def load_notes(filename) -> tuple:
    with open(filename, 'r') as file:
        data = json.load(file)
    return data['settings'], data['notes']

def check_note_hit(note, line_y) -> str:
    if note.progress >= NOTE_RADIUS - 10:
        if abs(note.y - line_y) <= NOTE_RADIUS * 1.25:
            return "perfect"
        elif abs(note.y - line_y) <= NOTE_RADIUS * 2.5:
            return "good"
    elif note.progress >= NOTE_RADIUS - 20:
        if abs(note.y - line_y) <= NOTE_RADIUS * 1.25:
            return "good"
        elif abs(note.y - line_y) <= NOTE_RADIUS * 2.5:
            return "bad"
    return None

def save_player(filepath, player_data):
    with open(filepath, 'w') as file:
        json.dump(player_data, file, indent=4)