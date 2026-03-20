import csv
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from cs50 import SQL
from src import reddy_tech
from src.text_classifier import load_text_model, get_vocab

DB_PATH = root / 'src' / 'main.db'
OUT_CSV = root / 'exported_posts.csv'

def export_all():
    db = SQL(f"sqlite:///{DB_PATH}")
    rows = []
    # list tables (user tables) could be many; query users table for usernames
    users = db.execute('SELECT username FROM users')
    model = load_text_model()
    word_to_index, max_len = get_vocab()
    for u in users:
        uname = u['username']
        try:
            posts = db.execute('SELECT * FROM :tablename', tablename=uname)
        except Exception:
            continue
        for p in posts:
            text = p.get('text','')
            cleaned = reddy_tech.clean_text(text)
            X = reddy_tech.sentences_to_indices([cleaned], word_to_index, max_len)
            score = None
            try:
                score = float(model.predict(X)[0][0])
            except Exception:
                score = ''
            rows.append({'username': uname, 'text': text, 'cleaned': cleaned, 'score': score, 'timestamp': p.get('timestamp','')})

    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['username','text','cleaned','score','timestamp'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print('Exported', len(rows), 'rows to', OUT_CSV)

if __name__ == '__main__':
    export_all()
