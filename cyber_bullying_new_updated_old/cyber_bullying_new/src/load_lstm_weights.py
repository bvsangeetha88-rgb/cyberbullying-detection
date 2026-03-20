"""
Helper to reconstruct the LSTM model architecture (as used in the notebook) and load weights
from an HDF5 file that contains only `model_weights` (no model config).

Run from project root (where `src/` is a subfolder):
    python src/load_lstm_weights.py

This script will:
 - inspect `src/LSTM.h5` to find dataset shapes
 - infer embedding dimension and final Dense output dim
 - build a compatible model and call `model.load_weights(...)`
 - print model.summary()

Note: This attempts to reconstruct the architecture used in the notebook (two LSTM layers,
embedding + dropout). If the original architecture differs, loading weights may still fail.
"""
from pathlib import Path
import h5py
import sys

MODEL_PATH = Path('src/LSTM.h5')
if not MODEL_PATH.exists():
    print(f"Model file not found: {MODEL_PATH.resolve()}")
    sys.exit(1)

print(f"Inspecting: {MODEL_PATH}\n")
with h5py.File(str(MODEL_PATH), 'r') as f:
    if 'model_weights' not in f:
        print("HDF5 file does not contain 'model_weights' group. It may be a full SavedModel or corrupted.")
        print('Top-level keys:', list(f.keys()))
        sys.exit(1)
    mw = f['model_weights']
    datasets = []
    def visitor(name, obj):
        if isinstance(obj, h5py.Dataset):
            datasets.append((name, obj.shape))
    mw.visititems(visitor)

print('Found datasets (name, shape) under model_weights:')
for name, shape in datasets:
    print('-', name, shape)

# Heuristics: find largest 2D dataset -> embedding weights, find dense kernel -> final Dense
embedding_shape = None
dense_out = None
for name, shape in datasets:
    if len(shape) == 2:
        # candidate for embedding (vocab, emb_dim) or dense (in, out)
        if embedding_shape is None or shape[0] > embedding_shape[0]:
            embedding_shape = shape
        # if name contains 'dense' or 'dense_' or 'dense/kernel' prefer it for final dense
        if 'dense' in name.lower() and (dense_out is None or shape[1] > dense_out):
            dense_out = shape[1]

print('\nGuessed embedding shape:', embedding_shape)
print('Guessed final dense output dim:', dense_out)

# Now try to reconstruct model and load weights
try:
    from tensorflow.keras.models import Model
    from tensorflow.keras.layers import Input, Embedding, LSTM, Dropout, Dense
    from src import reddy_tech

    word_to_index, max_len = reddy_tech.init()
    vocab_len = len(word_to_index) + 1
    if embedding_shape is None:
        print('Could not detect embedding shape from weights; aborting model reconstruction.')
        sys.exit(1)
    emb_dim = embedding_shape[1]
    print(f'Building model with vocab_len={vocab_len}, max_len={max_len}, emb_dim={emb_dim}')

    sentence_indices = Input(shape=(max_len,), dtype='int32')
    embedding_layer = Embedding(input_dim=vocab_len, output_dim=emb_dim, trainable=False)
    embeddings = embedding_layer(sentence_indices)
    X = LSTM(128, return_sequences=True)(embeddings)
    X = Dropout(0.5)(X)
    X = LSTM(128, return_sequences=False)(X)
    X = Dropout(0.5)(X)

    # decide output units based on detected dense_out
    if dense_out is None:
        print('Could not detect final dense output dimension. Defaulting to 1 (sigmoid).')
        out_units = 1
    else:
        out_units = int(dense_out)

    if out_units == 1:
        out = Dense(1, activation='sigmoid')(X)
    else:
        out = Dense(out_units, activation='softmax')(X)

    model = Model(inputs=sentence_indices, outputs=out)
    print('\nModel built. Attempting to load weights...')
    model.load_weights(str(MODEL_PATH))
    print('Weights loaded successfully. Model summary:')
    model.summary()
except Exception as e:
    print('Failed to reconstruct and load weights:', e)
    import traceback; traceback.print_exc()
    sys.exit(2)

print('\nDone.')
