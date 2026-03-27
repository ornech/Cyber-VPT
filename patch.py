import json

file_path = 'mitre_v2_vectorized.json'

# 1. On charge la bibliothèque
with open(file_path, 'r', encoding='utf-8') as f:
    library = json.load(f)

# 2. On cherche la technique T1059 et on injecte le vecteur parfait
for entry in library:
    if entry['tid'] == 'T1059':
        print(f"Avant : {entry['v_vector']}")
        entry['v_vector'] = [0.8, 0.9, 0.7, 1.0, 0.6] # Notre vecteur expert
        print(f"Après : {entry['v_vector']}")
        break

# 3. On sauvegarde
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(library, f, indent=4, ensure_ascii=False)

print("\n✅ Patch appliqué avec succès sur T1059 !")