from pathlib import Path
import h5py
import traceback

MODEL_FULL = Path('src/LSTM_full.h5')
MODEL_WEIGHTS = Path('src/LSTM.h5')

_model = None
_vocab = None

def _inspect_weights(path):
    """Return guessed (embedding_shape, final_dense_out) from weights file."""
    with h5py.File(str(path), 'r') as f:
        if 'model_weights' not in f:
            return None, None
        datasets = []
        def visitor(name, obj):
            if isinstance(obj, h5py.Dataset):
                datasets.append((name, obj.shape))
        f['model_weights'].visititems(visitor)
    embedding_shape = None
    dense_out = None
    for name, shape in datasets:
        if len(shape) == 2:
            if embedding_shape is None or shape[0] > embedding_shape[0]:
                embedding_shape = shape
            if 'dense' in name.lower() and (dense_out is None or shape[1] > dense_out):
                dense_out = shape[1]
    return embedding_shape, dense_out

def load_text_model():
    """Load and return a Keras model for text classification.

    Strategy:
    - If `src/LSTM_full.h5` exists, load it with `load_model` (contains architecture+weights).
    - Else, try `load_model` on `src/LSTM.h5` (may fail if weights-only).
    - Else, reconstruct architecture (based on notebook) and load weights from `src/LSTM.h5`.
    """
    global _model
    if _model is not None:
        return _model

    try:
        from tensorflow.keras.models import load_model
    except Exception as e:
        raise RuntimeError('TensorFlow/Keras is required to load the model: ' + str(e))

    # Preferred: full model file
    try:
        if MODEL_FULL.exists():
            _model = load_model(str(MODEL_FULL))
            # Re-compile the model to ensure a deterministic state for inference
            _model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            return _model
    except Exception:
        print('Failed to load full model, trying fallback...')
        traceback.print_exc()

    # Try loading weights-containing file directly (may be full model or weights-only)
    try:
        if MODEL_WEIGHTS.exists():
            # Attempt to load as full model first
            try:
                _model = load_model(str(MODEL_WEIGHTS))
                # Re-compile the model to ensure a deterministic state for inference
                _model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
                return _model
            except Exception:
                # Will attempt reconstruct + load_weights
                pass
    except Exception:
        traceback.print_exc()

    # Reconstruct architecture and load weights
    try:
        # lazy-import reddy_tech to get vocab and max_len
        from src import reddy_tech
        word_to_index, max_len = reddy_tech.init()
        vocab_len = len(word_to_index) + 1

        # inspect weights file to guess embedding dim and output units
        emb_shape, dense_out = _inspect_weights(MODEL_WEIGHTS)
        if emb_shape is None:
            raise RuntimeError('Could not detect embedding shape in weights file')
        emb_dim = int(emb_shape[1])
        out_units = int(dense_out) if dense_out is not None else 1

        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import Input, Embedding, LSTM, Dropout, Dense

        sentence_indices = Input(shape=(max_len,), dtype='int32')
        embedding_layer = Embedding(input_dim=vocab_len, output_dim=emb_dim, trainable=False)
        embeddings = embedding_layer(sentence_indices)
        X = LSTM(128, return_sequences=True)(embeddings)
        X = Dropout(0.5)(X)
        X = LSTM(128, return_sequences=False)(X)
        X = Dropout(0.5)(X)
        if out_units == 1:
            out = Dense(1, activation='sigmoid')(X)
        else:
            out = Dense(out_units, activation='softmax')(X)
        model = Model(inputs=sentence_indices, outputs=out)
        model.load_weights(str(MODEL_WEIGHTS))
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        _model = model
        return _model
    except Exception as e:
        traceback.print_exc()
        raise RuntimeError('Failed to reconstruct/load weights: ' + str(e))

def get_vocab():
    """Return (word_to_index, max_len) using `reddy_tech.init()`.
    This is separated so callers can always obtain consistent preprocessing parameters.
    """
    global _vocab
    if _vocab is not None:
        return _vocab
    from src import reddy_tech
    _vocab = reddy_tech.init()
    return _vocab
