import json

def add_ids_to_notes(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    
    valid_index = 1
    for note in data["notes"]:
        if "x" in note and "y" in note and "note_expand_speed" in note:
            note_with_id = {"id": valid_index}
            note_with_id.update(note)
            note.clear()
            note.update(note_with_id)
            valid_index += 1
    
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    add_ids_to_notes("./notes.json")