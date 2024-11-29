import json

def remove_ids_from_notes(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    
    for note in data["notes"]:
        if "id" in note:
            del note["id"]
    
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    remove_ids_from_notes("./notes.json")