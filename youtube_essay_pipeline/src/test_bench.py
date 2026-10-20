import time
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# Test speed of full frame vs patch
width, height = 1920, 1080
frame = np.zeros((height, width, 3), dtype=np.uint8)

# Create dummy caption overlay
font = ImageFont.truetype(r"C:\Windows\Fonts\ariali.ttf", 40)
text = "The Phantom of the Railway Crossing"

# Bounding box
bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
x1 = (width - tw) // 2 - 10
y1 = 920 - 10
x2 = x1 + tw + 20
y2 = y1 + th + 20

# Create patch only
patch_img = Image.new("RGBA", (x2 - x1, y2 - y1), (0, 0, 0, 0))
d = ImageDraw.Draw(patch_img)
d.text((10, 10), text, font=font, fill=(255, 230, 0, 204))
patch_np = np.array(patch_img)
patch_alpha = (patch_np[:, :, 3:4] / 255.0).astype(np.float32)
patch_bgr = patch_np[:, :, [2, 1, 0]].astype(np.float32)

t0 = time.time()
for _ in range(100):
    # Full frame zoom
    resized = cv2.resize(frame, (1960, 1102), interpolation=cv2.INTER_LINEAR)
    crop = resized[11:1091, 20:1940]
    # Patch blend
    crop[y1:y2, x1:x2] = (crop[y1:y2, x1:x2] * (1.0 - patch_alpha) + patch_bgr * patch_alpha).astype(np.uint8)
t1 = time.time()
fps = 100 / (t1 - t0)
print(f"Optimized Patch FPS: {fps:.1f} fps (100 frames in {t1-t0:.3f}s)")
