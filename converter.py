import json

with open('cenz.txt', 'r', encoding='utf-8') as f:
    cenz = [i.rstrip() for i in f]

    with open('cenz.json', 'w', encoding='utf-8') as f:
        json.dump(cenz, f, ensure_ascii=False)

