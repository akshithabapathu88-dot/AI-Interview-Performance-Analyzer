from PIL import Image, ImageDraw, ImageFont
import os

width = 256
height = 256
img = Image.new('RGBA', (width, height), (8, 20, 40, 255))
draw = ImageDraw.Draw(img)

# Gradient background
for y in range(height):
    t = y / (height - 1)
    r = int(8 + (26 - 8) * t)
    g = int(20 + (84 - 20) * t)
    b = int(40 + (132 - 40) * t)
    draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

# Circle accent
circle_box = [width*0.15, height*0.1, width*0.85, height*0.8]
draw.ellipse(circle_box, outline=(115, 210, 255, 255), width=18)

draw.ellipse([width*0.35, height*0.25, width*0.65, height*0.55], fill=(255,255,255,255))

# AI text
try:
    font = ImageFont.truetype('arial.ttf', 96)
except Exception:
    font = ImageFont.load_default()
text = 'AI'
try:
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
except AttributeError:
    bbox = font.getbbox(text)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(((width - w) / 2, height * 0.55), text, font=font, fill=(255,255,255,255))

output_path = os.path.join('public', 'favicon.ico')
img.save(output_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
print('saved', output_path)
