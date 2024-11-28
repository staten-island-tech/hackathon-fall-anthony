import json, os

NOTE_RADIUS = 45

def create_player(filename) -> None:
    with open(filename, "w", errors="ignore") as file:
        json.dump(
            {
                "previous_score": 0,
                "previous_rating": "N/A",
                "previous_accuracy": 0,
                "best_score": 0,
                "best_rating": "N/A",
                "best_accuracy": 0
            },
            file,
            indent=4
        )

def load_player(filename) -> dict:
    if not os.path.exists(filename):
        create_player(filename)
    with open(filename, "r", errors="ignore") as file:
        data = json.load(file)
    return data

def load_notes(filename) -> tuple:
    with open(filename, "r", errors="ignore") as file:
        data = json.load(file)
    return data["settings"], data["notes"]

def check_note_hit(note, line_y, line_speed) -> str:
    if note.progress >= NOTE_RADIUS - 10:
        if abs(note.y - line_y) <= NOTE_RADIUS * line_speed / 6:
            return "perfect"
        elif abs(note.y - line_y) <= NOTE_RADIUS * line_speed / 3:
            return "good"
    elif note.progress >= NOTE_RADIUS - 20:
        if abs(note.y - line_y) <= NOTE_RADIUS * line_speed / 6:
            return "good"
        elif abs(note.y - line_y) <= NOTE_RADIUS * line_speed / 3:
            return "bad"
    return None

def save_player(filepath, player_data) -> None:
    with open(filepath, "w", errors="ignore") as file:
        json.dump(player_data, file, indent=4)