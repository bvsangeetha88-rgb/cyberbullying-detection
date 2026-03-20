import os
from tempfile import mkdtemp

# Base directory of project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

# Tesseract command (set to full path if tesseract is not in PATH)
# Leave empty to rely on system PATH or set via env var TESSERACT_CMD
TESSERACT_CMD = os.getenv('TESSERACT_CMD', '')

# Telepot bot token - set via environment variable for safety
TELEPOT_TOKEN = os.getenv('TELEPOT_TOKEN', '')

# Flask session / debug helpers (optional)
DEBUG = True
TEMPLATES_AUTO_RELOAD = True
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"