import numpy as np
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from src.text_classifier import load_text_model, get_vocab

def nearest(word, embedding_matrix, word_to_index, k=10):
    idx = word_to_index.get(word)
    if idx is None:
        return None
    vec = embedding_matrix[idx]
    # compute cosine similarities
    norms = np.linalg.norm(embedding_matrix, axis=1)
    vec_norm = np.linalg.norm(vec)
    sims = (embedding_matrix @ vec) / (norms * (vec_norm + 1e-12))
    # get top k excluding itself
    top = np.argsort(-sims)
    res = []
    for i in top:
        if i == idx:
            continue
        res.append((i, float(sims[i])))
        if len(res) >= k:
            break
    # map indices back to words
    index_to_word = {v: k for k, v in word_to_index.items()}
    return [(index_to_word.get(i, '<UNK>'), score) for i, score in res]

def main():
    model = load_text_model()
    word_to_index, max_len = get_vocab()
    # get embedding layer weights
    try:
        emb_layer = None
        for layer in model.layers:
            if 'Embedding' in layer.__class__.__name__:
                emb_layer = layer
                break
        if emb_layer is None:
            print('No embedding layer found in model')
            return
        W = emb_layer.get_weights()[0]
        print('Embedding matrix shape:', W.shape)
    except Exception as e:
        print('Failed to extract embedding matrix:', e)
        return

    queries = ['kill', 'murder', 'attack', 'hate']
    for q in queries:
        print('\nQuery word:', q)
        q_lower = q.lower()
        if q_lower not in word_to_index:
            print(' - Not in vocabulary')
            continue
        neighbors = nearest(q_lower, W, word_to_index, k=10)
        if neighbors is None:
            print(' - nearest returned None')
            continue
        for w, s in neighbors:
            print(f'   {w:20s} {s:.4f}')

if __name__ == '__main__':
    main()
