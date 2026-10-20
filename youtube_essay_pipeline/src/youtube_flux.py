"""
youtube_flux.py - True Photorealistic Image Asset Generator with Locked Photo-Grade Liminal Horror Style
Strictly bans all vector drawings, programmatic shapes, and black ovals.
Enforces real API generation for every scene:
1. Primary: Hugging Face black-forest-labs/FLUX.1-schnell with strict HTTP status code and response header validation.
2. Secondary: High-speed photorealistic generative stream (model=sana / default) with negative prompt lock and PIL verification.
3. Every prompt uses the Golden Horror Prompt Template matching r9_b01_plate.jpg.
4. If image generation fails, raises a hard RuntimeError with clear diagnostics instead of saving corrupted files or drawing shapes.
"""

import os
import io
import re
import sys
import time
import urllib.parse
import requests
import cv2
import numpy as np
from PIL import Image

HF_TOKEN = os.environ.get("HUGGING_FACE_TOKEN", "")
POLLEN_KEY = os.environ.get("POLLINATIONS_API_KEY", "")

# 1. The Golden Horror Prompt Template Modifier
GOLDEN_HORROR_STYLE_MODIFIER = (
    ", authentic 1997 found footage camcorder capture, harsh overhead fluorescent tube lighting "
    "cutting through pitch-black absolute darkness, dense ominous forest or empty asphalt in background, "
    "heavy analog film grain, subtle chromatic aberration, raw unpolished cinematography, deep crushed shadows, "
    "eerie liminal space atmosphere, photorealistic 35mm photograph"
)

# 2. Negative Prompt Lock (bans clean studio art, vector, CGI, cartoons)
NEGATIVE_PROMPT = (
    "bright daylight, clean studio lighting, 3D render, cartoon, vector, "
    "illustration, blurry, oversaturated colors, text, watermark, CGI, modern digital art"
)

ASSETS_IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "images"))

def build_flux_prompt(scene_description: str) -> str:
    """
    Constructs the prompt using the Golden Horror formula:
    [SCENE DESCRIPTION HERE] + Golden Horror Style Modifier
    """
    cleaned_desc = scene_description.strip().rstrip(".,")
    return f"{cleaned_desc}{GOLDEN_HORROR_STYLE_MODIFIER}"

def is_valid_image_file(file_path: str, min_size: int = 30000) -> bool:
    """Verifies that a file exists, has sufficient size, and is an uncorrupted image."""
    if not os.path.exists(file_path):
        return False
    if os.path.getsize(file_path) < min_size:
        return False
    try:
        with Image.open(file_path) as im:
            im.verify()
        test_cv = cv2.imread(file_path)
        if test_cv is None or test_cv.shape[0] < 100 or test_cv.shape[1] < 100:
            return False
        return True
    except Exception:
        return False

def crop_and_clean_1080p(raw_img_path: str, output_path: str, width: int = 1920, height: int = 1080) -> str:
    """
    Crops any bottom watermark margin and resizes to pristine 1920x1080 Full HD (16:9).
    Ensures zero watermarks, zero logos, edge-to-edge scaling.
    """
    img = cv2.imread(raw_img_path)
    if img is None:
        raise RuntimeError(f"Corrupted image file cannot be read: {raw_img_path}")
        
    h, w = img.shape[:2]
    # Crop bottom 50px to eliminate any potential corner watermark
    cropped = img[:h - 50, :]
    
    # Scale to pristine 1920x1080 edge-to-edge Full HD
    final_1080p = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(output_path, final_1080p, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return output_path

def generate_via_huggingface_flux(full_prompt: str, temp_path: str, max_retries: int = 2) -> bool:
    """
    Sends request to black-forest-labs/FLUX.1-schnell.
    Strictly verifies HTTP status code == 200 and image headers.
    """
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "negative_prompt": NEGATIVE_PROMPT,
            "num_inference_steps": 4,
            "width": 1024,
            "height": 576
        }
    }
    
    for attempt in range(max_retries):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            content_type = res.headers.get("content-type", "")
            
            if res.status_code == 200 and ("image/" in content_type or len(res.content) > 30000):
                try:
                    img_buf = io.BytesIO(res.content)
                    with Image.open(img_buf) as img:
                        img.verify()
                    with open(temp_path, "wb") as f:
                        f.write(res.content)
                    print(f"[FLUX ENGINE] Hugging Face FLUX.1-schnell succeeded (Status: 200, Content-Type: {content_type})")
                    return True
                except Exception as verify_err:
                    print(f"[FLUX ENGINE] Corrupted buffer from HF: {verify_err}")
            else:
                print(f"[FLUX ENGINE] Hugging Face returned Status {res.status_code} ({content_type}): {res.text[:120]}")
                if res.status_code in (401, 403):
                    break
        except requests.exceptions.RequestException as req_err:
            print(f"[FLUX ENGINE] Hugging Face attempt {attempt + 1} error: {req_err}")
            
        time.sleep(2.0)
    return False

def generate_via_photorealistic_stream(full_prompt: str, temp_path: str, seed: int = 100, max_retries: int = 20) -> bool:
    """
    Generates real photorealistic frames via high-speed direct inference.
    Passes negative prompt lock and strictly verifies HTTP 200 and PIL image integrity.
    Persistently waits and retries through rate limits and public queue spikes.
    """
    encoded_prompt = urllib.parse.quote(full_prompt)
    encoded_neg = urllib.parse.quote(NEGATIVE_PROMPT)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    if POLLEN_KEY:
        headers["Authorization"] = f"Bearer {POLLEN_KEY}"
        
    endpoints = [
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?negative={encoded_neg}&model=flux&width=1280&height=720&nologo=true&seed={seed}",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?negative={encoded_neg}&model=sana&width=1280&height=720&nologo=true&seed={seed}",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?negative={encoded_neg}&width=1280&height=720&nologo=true&seed={seed}"
    ]
    
    for endpoint in endpoints:
        for attempt in range(max_retries):
            try:
                r = requests.get(endpoint, headers=headers, timeout=90)
                content_type = r.headers.get("content-type", "")
                
                if r.status_code == 200 and ("image/" in content_type or len(r.content) > 25000):
                    try:
                        buf = io.BytesIO(r.content)
                        with Image.open(buf) as im:
                            im.verify()
                        with open(temp_path, "wb") as f:
                            f.write(r.content)
                        print(f"[FLUX ENGINE] Image successfully generated. Pacing with 45s cooldown...")
                        time.sleep(45)
                        return True
                    except Exception as verify_err:
                        print(f"[FLUX ENGINE] Buffer verification error: {verify_err}")
                elif r.status_code in (402, 503):
                    print(f"[FLUX ENGINE] Stream rate limit {r.status_code} hit. Enforcing 45s cooldown sleep (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(45)
                else:
                    print(f"[FLUX ENGINE] Stream returned Status {r.status_code} ({content_type}). Cooling down 45s...")
                    time.sleep(45)
            except requests.exceptions.RequestException as err:
                print(f"[FLUX ENGINE] Stream connection error attempt {attempt + 1}: {err}. Waiting 45s...")
                time.sleep(45)
            except Exception as unk_err:
                print(f"[FLUX ENGINE] Unexpected fetch error attempt {attempt + 1}: {unk_err}. Waiting 45s...")
                time.sleep(45)
                
    return False

def generate_flux_image(base_prompt: str, output_path: str, width: int = 1920, height: int = 1080, seed: int = 100) -> str:
    """
    Generates a 100% photorealistic, gritty 16:9 cinematic still for the narration beat.
    Zero vector drawing, zero black ovals, zero watermarks.
    Throws a hard RuntimeError if real generation fails after all attempts.
    """
    if is_valid_image_file(output_path, min_size=40000):
        return output_path
    elif os.path.exists(output_path):
        print(f"[FLUX ENGINE] Purging outdated/corrupted cache file: {output_path}")
        try:
            os.remove(output_path)
        except Exception:
            pass

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    full_prompt = build_flux_prompt(base_prompt)
    temp_raw_path = output_path.replace(".jpg", "_raw.jpg")
    
    success = False
    
    # 1. Primary: Hugging Face FLUX.1-schnell with strict HTTP validation
    success = generate_via_huggingface_flux(full_prompt, temp_raw_path, max_retries=2)
    
    # 2. Secondary: High-speed photorealistic generative stream with negative prompt lock
    if not success:
        success = generate_via_photorealistic_stream(full_prompt, temp_raw_path, seed=seed, max_retries=25)
        
    # 3. Hard Error if no real image could be produced (ZERO VECTOR DRAWING FALLBACKS)
    if not success or not is_valid_image_file(temp_raw_path, min_size=25000):
        if os.path.exists(temp_raw_path):
            try:
                os.remove(temp_raw_path)
            except Exception:
                pass
        raise RuntimeError(
            f"[FATAL FLUX ERROR] Failed to generate photorealistic asset for prompt:\n'{base_prompt}'\n"
            f"API returned invalid data or exhausted retries. Geometric and vector fallbacks are banned."
        )
        
    # Crop any watermark margin and scale to pristine 1920x1080 16:9 Full HD
    clean_path = crop_and_clean_1080p(temp_raw_path, output_path, width, height)
    
    if os.path.exists(temp_raw_path) and temp_raw_path != output_path:
        try:
            os.remove(temp_raw_path)
        except Exception:
            pass
            
    print(f"[FLUX ASSET ENGINE] Produced pristine 16:9 photorealistic still: {os.path.basename(output_path)}")
    return clean_path

if __name__ == "__main__":
    test_out = os.path.join(ASSETS_IMAGE_DIR, "test_golden_horror.jpg")
    p = "A lone pedestrian standing under a flickering streetlamp on an empty rural road at midnight"
    res = generate_flux_image(p, test_out, seed=88)
    print("Golden horror test still saved successfully ->", res)
