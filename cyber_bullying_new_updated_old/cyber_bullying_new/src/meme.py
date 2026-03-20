

from PIL import Image, ImageDraw, ImageFont
import textwrap, os

def meme(para = 'Hello, World!'):
    # INPUT
    im = Image.open('static/meme/cat.jpg')

    # CONFIGURATION
    image_width, image_height = im.size
    draw = ImageDraw.Draw(im)

    def _load_font(preferred='arial.ttf', size=120):
        try:
            return ImageFont.truetype(preferred, size=size)
        except Exception:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size=size)
            except Exception:
                return ImageFont.load_default()

    def _fit_font_for_text(draw_obj, text, max_width, start_size=120, min_size=10):
        # Try decreasing sizes until the text fits the max_width
        size = start_size
        while size >= min_size:
            font = _load_font(size=size)
            w, h = _text_size(draw_obj, text, font)
            if w <= max_width:
                return font, (w, h)
            size -= 4
        # fallback to smallest font
        font = _load_font(size=min_size)
        return font, _text_size(draw_obj, text, font)
    shadowcolor = 'black'
    fillcolor = 'white'
    highlight_width = 5

    # MULTILINE
    paragraph = textwrap.wrap(str(para), initial_indent = '(output) ', placeholder = 'etc etc ...', width = 25, max_lines = 3, break_long_words = True)
    initial_height, line_spacing = (0.01 * image_height), 1
    def _text_size(draw_obj, text, font):
        """Return (width, height) of rendered text in a Pillow-version compatible way."""
        # Preferred: ImageDraw.textbbox (Pillow >= 8.0)
        try:
            bbox = draw_obj.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            return w, h
        except Exception:
            pass
        # Fallback: ImageDraw.textsize (older Pillow)
        try:
            return draw_obj.textsize(text, font=font)
        except Exception:
            pass
        # Fallback: ImageFont.getbbox / getsize
        try:
            bbox = font.getbbox(text)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            return w, h
        except Exception:
            pass
        try:
            return font.getsize(text)
        except Exception:
            # Last resort: estimate
            return (len(text) * font.size // 2, font.size)

    max_text_width = int(image_width * 0.9)
    for line in paragraph:
        # choose a font size that fits the image width
        arial, (text_width, text_height) = _fit_font_for_text(draw, line, max_text_width, start_size=120)
        x_coordinate, y_coordinate = (image_width - text_width) / 2, initial_height
        draw.text((x_coordinate - highlight_width, y_coordinate - highlight_width), line, font = arial, fill=shadowcolor)
        draw.text((x_coordinate + highlight_width, y_coordinate - highlight_width), line, font = arial, fill=shadowcolor)
        draw.text((x_coordinate - highlight_width, y_coordinate + highlight_width), line, font = arial, fill=shadowcolor)
        draw.text((x_coordinate + highlight_width, y_coordinate + highlight_width), line, font = arial, fill=shadowcolor)
        draw.text((x_coordinate, y_coordinate), line, font = arial, fill = fillcolor)
        initial_height += text_height + line_spacing

    # OUTPUT
    im.save('static/meme/output.png', "PNG")