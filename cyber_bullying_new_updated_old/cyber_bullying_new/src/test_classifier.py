from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from src.text_classifier import load_text_model, get_vocab
from src import reddy_tech

def predict_texts(texts):
    model = load_text_model()
    word_to_index, max_len = get_vocab()
    processed = [reddy_tech.clean_text(t) for t in texts]
    X = reddy_tech.sentences_to_indices(processed, word_to_index, max_len)
    preds = model.predict(X)
    for t, p in zip(texts, preds):
        print(f'Input: {t!r} -> cleaned: {processed.pop(0)!r} -> score: {p[0]:.4f}')

if __name__ == '__main__':
    samples = [
        'kill',
        'I will kill you',
        'murder',
        'He tried to attack me',
        'I love you',
        'You are great'
    ]
    predict_texts(samples)
