
import json
import shutil

# File paths
original_file = './notes.json'
backup_file = './backup.json'

# Backup the original notes.json
shutil.copyfile(original_file, backup_file)

with open(original_file, 'r') as file:
    data = json.load(file)

filtered_notes = [note for note in data['notes'] if 'line_speed' in note]

for note in filtered_notes:
    if 'id' in note:
        del note['id']

data['notes'] = filtered_notes

with open(original_file, 'w') as file:
    json.dump(data, file, indent=4)

print(f"Backup created at {backup_file} and cleaned notes saved to {original_file}.")