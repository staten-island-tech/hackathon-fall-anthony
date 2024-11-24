import json

def sort_notes_by_time(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    
    data['notes'].sort(key=lambda note: note['time'])
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    sort_notes_by_time('./notes.json')