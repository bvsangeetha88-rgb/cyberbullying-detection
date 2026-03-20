import sys, traceback
from pathlib import Path
MODEL = Path('src/LSTM.h5')
if not MODEL.exists():
    print(f"Model file not found: {MODEL}")
    sys.exit(1)

print(f"Inspecting model file: {MODEL}\n")

# First try to load with TensorFlow / Keras
try:
    from tensorflow.keras.models import load_model
    m = load_model(str(MODEL))
    print("Successfully loaded model with TensorFlow/Keras.\nModel summary:\n")
    m.summary()
    print('\nLayers:')
    for i, layer in enumerate(m.layers):
        try:
            out_shape = layer.output_shape
        except Exception:
            out_shape = None
        print(f"{i}. name={layer.name}, class={layer.__class__.__name__}, output_shape={out_shape}")
    sys.exit(0)
except Exception as e:
    print("Could not load model with TensorFlow/Keras:", e)
    # traceback.print_exc()

# Fallback: inspect HDF5 structure with h5py
try:
    import h5py
    with h5py.File(str(MODEL), 'r') as f:
        print('\nHDF5 top-level groups:')
        for key in f.keys():
            print(' -', key)
        print('\nListing structure (first 3 levels):')
        def list_group(g, prefix='', depth=0, maxdepth=3):
            if depth > maxdepth:
                return
            for k, v in g.items():
                print(prefix + '/' + k)
                if isinstance(v, h5py.Group):
                    list_group(v, prefix + '/' + k, depth+1, maxdepth)
        list_group(f, '')
        print('\nAttributes at root:')
        for k, v in f.attrs.items():
            print(' -', k, ':', v)
    sys.exit(0)
except Exception as e2:
    print('Failed to inspect with h5py as well:', e2)
    traceback.print_exc()
    sys.exit(2)
