"""
render_video.py - High-Bitrate Cinematic Analog Horror Video Renderer
Precision Overhaul:
1. Dynamic 3-Second Room Title Flash (center-top with smooth fade-out, zero permanent headlines)
2. Clean, highly readable Arial Bold 58px Captions with 8px black stroke, crisp white text,
   soft amber (#FFD166) and crimson (#FF4D4D) alert highlights at y=1520px
3. Subtle 10%-15% Film Grain & Analog Noise Filter via FFmpeg: -vf "noise=alls=15:allf=t+u,format=yuv420p"
4. Smooth 3D Camcorder Motion (Walk-In Zoom 1.0x-1.16x, Pan/Drift) + SIMD Flashlight Vignette Breathing
5. Strict duration (120s - 210s) and file size (25MB - 50MB)
"""

import os
import sys
import json
import math
import subprocess
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1920
FPS = 30

CRIMSON_KEYWORDS = {
    "fatal", "mimic", "entities", "entity", "shadow", "suction", "rupture", "burns",
    "predators", "predator", "deadzone", "never", "avoid", "dehydration", "memory",
    "loss", "mannequin", "displacement", "subterranean", "crimson", "radiation",
    "harvester", "extinguish", "prohibited", "death", "boiling", "monsters", "trap"
}

AMBER_KEYWORDS = {
    "probability", "anomalies", "chlorine", "zero", "0.01%", "31%", "78%", "sirens",
    "survive", "survival", "safe", "door", "walkway", "exit", "minutes", "stairs",
    "loading", "warning", "caution", "seconds", "lockout", "clean", "condensation",
    "stockrooms", "canned", "rations", "protocol", "level"
}

def get_pil_font(size: int, bold: bool = True):
    paths = [
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\consolab.ttf" if bold else "C:\\Windows\\Fonts\\consola.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def precompute_big_flashlight_mask(pad: int = 120) -> np.ndarray:
    """Pre-computes an oversized flashlight mask with baked scanlines for instant cv2.multiply SIMD."""
    big_h = HEIGHT + 2 * pad
    big_w = WIDTH + 2 * pad
    cy, cx = big_h / 2.0, big_w / 2.0
    radius = 700.0
    y, x = np.ogrid[:big_h:4, :big_w:4]
    dist_sq = (x - cx/4)**2 + (y - cy/4)**2
    r_sq = (radius / 4)**2
    mask = 1.05 - 0.35 * np.clip(dist_sq / r_sq, 0.0, 1.0)
    mask = cv2.resize(mask.astype(np.float32), (big_w, big_h), interpolation=cv2.INTER_LINEAR)
    
    # Subtle scanlines (odd rows at 97% brightness)
    mask[1::2] *= 0.97
    
    mask_u8 = np.clip(mask * 200.0, 0, 255).astype(np.uint8)
    return np.dstack([mask_u8, mask_u8, mask_u8])

BIG_FLASHLIGHT_MASK = precompute_big_flashlight_mask(pad=120)

def apply_chromatic_aberration(bgr: np.ndarray, shift: int = 2) -> np.ndarray:
    """Subtle 2px edge RGB chromatic shift for authentic analog camcorder feel."""
    out = bgr.copy()
    out[:, shift:, 0] = bgr[:, :-shift, 0]   # Blue shifted right
    out[:, :-shift, 2] = bgr[:, shift:, 2]   # Red shifted left
    return out

class PreRenderedPatch:
    """Tightly cropped, pre-rendered RGBA overlay patch with float alpha blending and smooth fade support."""
    def __init__(self, pil_overlay: Image.Image, x_offset: int = 0, y_offset: int = 0):
        arr = np.array(pil_overlay)
        alpha = arr[:, :, 3]
        non_zero = np.where(alpha > 0)
        if len(non_zero[0]) == 0:
            self.empty = True
            return
            
        self.empty = False
        y_min, y_max = int(non_zero[0].min()), int(non_zero[0].max()) + 1
        x_min, x_max = int(non_zero[1].min()), int(non_zero[1].max()) + 1
        
        crop_arr = arr[y_min:y_max, x_min:x_max]
        self.y1 = y_offset + y_min
        self.y2 = y_offset + y_max
        self.x1 = x_offset + x_min
        self.x2 = x_offset + x_max
        
        self.alpha_f = (crop_arr[:, :, 3:4].astype(np.float32)) / 255.0
        self.one_minus_alpha = 1.0 - self.alpha_f
        self.bgr_f = crop_arr[:, :, [2, 1, 0]].astype(np.float32)
        self.premult_f = self.bgr_f * self.alpha_f

    def blit(self, base_bgr: np.ndarray, alpha_scale: float = 1.0):
        if self.empty or alpha_scale <= 0.01:
            return
        sub = base_bgr[self.y1:self.y2, self.x1:self.x2]
        if alpha_scale >= 0.99:
            base_bgr[self.y1:self.y2, self.x1:self.x2] = (
                sub.astype(np.float32) * self.one_minus_alpha + self.premult_f
            ).astype(np.uint8)
        else:
            cur_alpha = self.alpha_f * alpha_scale
            base_bgr[self.y1:self.y2, self.x1:self.x2] = (
                sub.astype(np.float32) * (1.0 - cur_alpha) + self.bgr_f * cur_alpha
            ).astype(np.uint8)

def pre_render_room_title_flash(room_name: str, is_deadzone: bool, font_title: ImageFont.ImageFont) -> PreRenderedPatch:
    """
    Pre-renders a cinematic horror title card in the center-top.
    Flashes for exactly 3.0 seconds when entering a new room/option, then fades out completely.
    """
    img = Image.new("RGBA", (WIDTH, 320), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    y = 160
    max_w = 980
    bbox = draw.textbbox((0, 0), room_name, font=font_title)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    card_w = min(max_w, max(tw + 80, 520))
    card_h = 80
    x1 = (WIDTH - card_w) // 2
    y1 = y
    x2 = x1 + card_w
    y2 = y1 + card_h
    
    # Border & Dark glass background
    border_color = (255, 77, 77, 245) if is_deadzone else (255, 209, 102, 245)
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=16, fill=(12, 14, 18, 235), outline=border_color, width=2)
    
    # Text centered
    tx = x1 + (card_w - tw) // 2
    ty = y1 + (card_h - th) // 2 - 3
    draw.text((tx, ty), room_name, font=font_title, fill=(255, 255, 255, 255))
    
    return PreRenderedPatch(img, 0, 0)

def pre_render_hook_ui(title: str, font_title: ImageFont.ImageFont, font_count: ImageFont.ImageFont) -> tuple:
    """Pre-renders title banner and countdown boxes for seconds 1 to 5."""
    img_title = Image.new("RGBA", (WIDTH, 420), (0, 0, 0, 0))
    d_t = ImageDraw.Draw(img_title)
    
    f_size = 36
    cur_font = get_pil_font(f_size, bold=True)
    while f_size > 22:
        bbox = d_t.textbbox((0, 0), title, font=cur_font)
        if (bbox[2] - bbox[0]) <= 860:
            break
        f_size -= 2
        cur_font = get_pil_font(f_size, bold=True)
        
    t_bbox = d_t.textbbox((0, 0), title, font=cur_font)
    tw = t_bbox[2] - t_bbox[0]
    th = t_bbox[3] - t_bbox[1]
    
    banner_w = min(960, max(tw + 60, 520))
    banner_h = 76
    bx1 = (WIDTH - banner_w) // 2
    by1 = 250
    bx2 = bx1 + banner_w
    by2 = by1 + banner_h
    
    d_t.rectangle([(bx1, by1), (bx2, by2)], fill=(12, 14, 18, 235), outline=(255, 209, 102, 245), width=2)
    d_t.text((bx1 + (banner_w - tw)//2, by1 + (banner_h - th)//2 - 3), title, font=cur_font, fill=(255, 255, 255, 255))
    patch_title = PreRenderedPatch(img_title, 0, 0)
    
    # Countdown boxes at y=1380..1470
    countdown_patches = {}
    cy = 1380
    for sec in range(1, 6):
        img_c = Image.new("RGBA", (WIDTH, 1500), (0, 0, 0, 0))
        d_c = ImageDraw.Draw(img_c)
        count_str = f"LOCKOUT IN: 0{sec}"
        c_bbox = d_c.textbbox((0, 0), count_str, font=font_count)
        cw = c_bbox[2] - c_bbox[0]
        ch = c_bbox[3] - c_bbox[1]
        draw_w = cw + 80
        cx1 = (WIDTH - draw_w) // 2
        cx2 = cx1 + draw_w
        d_c.rectangle([(cx1, cy), (cx2, cy + 86)], fill=(18, 12, 12, 235), outline=(255, 77, 77, 245), width=2)
        d_c.text(((WIDTH - cw)//2, cy + (86 - ch)//2 - 3), count_str, font=font_count, fill=(255, 77, 77, 255))
        countdown_patches[sec] = PreRenderedPatch(img_c, 0, 0)
        
    return patch_title, countdown_patches

def pre_render_caption(caption_text: str, font_cap: ImageFont.ImageFont) -> PreRenderedPatch:
    """
    Clean, universally readable Arial Bold 58px caption at y=1520px.
    Crisp #FFFFFF text with 8px black stroke, soft amber (#FFD166) and crimson (#FF4D4D) alert highlights.
    """
    words = caption_text.split()
    if not words:
        return PreRenderedPatch(Image.new("RGBA", (10, 10), (0, 0, 0, 0)))
        
    img = Image.new("RGBA", (WIDTH, 1720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    word_gap = 26
    y = 1520
    
    word_widths = []
    for w in words:
        bbox = draw.textbbox((0, 0), w, font=font_cap)
        w_w = bbox[2] - bbox[0]
        word_widths.append(w_w)
        
    total_w = sum(word_widths) + (len(words) - 1) * word_gap
    start_x = (WIDTH - total_w) // 2
    
    curr_x = start_x
    for idx, w in enumerate(words):
        clean_word = "".join(ch for ch in w.lower() if ch.isalnum() or ch in "%")
        
        if clean_word in CRIMSON_KEYWORDS:
            text_color = (255, 77, 77, 255)   # Crimson #FF4D4D
        elif clean_word in AMBER_KEYWORDS:
            text_color = (255, 209, 102, 255) # Soft Amber #FFD166
        else:
            text_color = (255, 255, 255, 255) # Crisp White #FFFFFF
            
        # Clean 8px black stroke for universal readability
        draw.text(
            (curr_x, y),
            w,
            font=font_cap,
            fill=text_color,
            stroke_width=8,
            stroke_fill=(0, 0, 0, 255)
        )
        curr_x += word_widths[idx] + word_gap
        
    return PreRenderedPatch(img, 0, 0)

def build_video_frames(
    script_data: dict,
    timeline: list,
    caption_chunks: list,
    scenes_dir: str,
    master_audio_path: str,
    output_mp4_path: str
):
    """
    Renders video at locked 30 FPS with:
    - Dynamic 3-second room flashes (fading out for 100% clean upper screen)
    - Clean Arial 58px captions with 8px black stroke
    - Subtle 15% film grain overlay (-vf noise=alls=15:allf=t+u,format=yuv420p)
    - Directly piped to FFmpeg H.264
    """
    total_duration = timeline[-1]["end_time"]
    total_frames = int(math.ceil(total_duration * FPS))
    print(f"[RENDER] Total video frames to render: {total_frames} ({total_duration:.2f}s at {FPS} FPS)")
    
    # 1. Load and cache all scene background images
    loaded_images = {}
    for item in timeline:
        sc_id = item["scene_id"]
        if sc_id not in loaded_images:
            img_p = os.path.join(scenes_dir, f"{sc_id}.jpg")
            if os.path.exists(img_p):
                img_cv = cv2.imread(img_p)
                if img_cv is not None and img_cv.shape[:2] != (HEIGHT, WIDTH):
                    img_cv = cv2.resize(img_cv, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
                loaded_images[sc_id] = img_cv
            else:
                print(f"[RENDER] WARNING: Image not found: {img_p}. Creating fallback.")
                loaded_images[sc_id] = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
                
    # 2. Pre-render UI Overlays
    print("[RENDER] Pre-rendering fonts, 3-second room flashes, and clean Arial captions...")
    font_room_title = get_pil_font(34, bold=True)
    font_hook_title = get_pil_font(38, bold=True)
    font_count = get_pil_font(44, bold=True)
    font_captions = get_pil_font(58, bold=True) # Clean Arial Bold 58px
    
    # Pre-render 3-second room flash cards (Option 1, Option 2, Option 3)
    room_flashes = {}
    for item in timeline:
        if item.get("is_option_start"):
            opt_idx = item.get("option_index", 1)
            opt_name = item.get("option_name", f"OPTION {opt_idx}")
            is_deadzone = item.get("is_deadzone", False)
            room_flashes[opt_idx] = {
                "start_time": item["start_time"],
                "patch": pre_render_room_title_flash(opt_name, is_deadzone, font_room_title)
            }
            
    title_text = script_data.get("title", "CHOOSE ONE TO SURVIVE")
    hook_title_patch, countdown_patches = pre_render_hook_ui(title_text, font_hook_title, font_count)
    
    print(f"[RENDER] Pre-rendering {len(caption_chunks)} clean Arial 58px captions...")
    caption_patches = [pre_render_caption(c["text"], font_captions) for c in caption_chunks]
    print("[RENDER] Pre-rendering complete! Launching FFmpeg with 15% film grain overlay...")
    
    # 3. Launch FFmpeg with 15% film grain filter
    os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "bgr24",
        "-r", str(FPS),
        "-i", "-",  # Video from stdin pipe
        "-i", master_audio_path,
        "-vf", "noise=alls=15:allf=t+u,format=yuv420p", # Subtle 15% authentic cinematic film grain
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-b:v", "1350k",
        "-maxrate", "1800k",
        "-bufsize", "3600k",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        output_mp4_path
    ]
    
    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    caption_idx = 0
    num_captions = len(caption_chunks)
    pad = 120
    
    start_time = time.time()
    
    for f in range(total_frames):
        current_time = f / float(FPS)
        
        # A. Active Scene
        active_scene = timeline[0]
        for item in timeline:
            if item["start_time"] <= current_time <= item["end_time"]:
                active_scene = item
                break
                
        sc_id = active_scene["scene_id"]
        base_img = loaded_images.get(sc_id)
        if base_img is None:
            base_img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            
        # B. Smooth 3D Camcorder Motion (Walk-in zoom 1.0x -> 1.16x, Pan/drift)
        sc_start = active_scene["start_time"]
        sc_dur = max(0.1, active_scene["total_duration"])
        t_prog = min(1.0, max(0.0, (current_time - sc_start) / sc_dur))
        
        scene_hash = hash(sc_id) % 3
        if scene_hash == 0:
            scale = 1.0 + 0.16 * t_prog
            crop_w = int(WIDTH / scale)
            crop_h = int(HEIGHT / scale)
            x_start = (WIDTH - crop_w) // 2
            y_start = (HEIGHT - crop_h) // 2
            cropped = base_img[y_start:y_start+crop_h, x_start:x_start+crop_w]
            frame_bgr = cv2.resize(cropped, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
        elif scene_hash == 1:
            scale = 1.10
            crop_w = int(WIDTH / scale)
            crop_h = int(HEIGHT / scale)
            max_pan_x = WIDTH - crop_w
            x_start = int(max_pan_x * t_prog)
            y_start = (HEIGHT - crop_h) // 2
            cropped = base_img[y_start:y_start+crop_h, x_start:x_start+crop_w]
            frame_bgr = cv2.resize(cropped, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
        else:
            scale = 1.10
            crop_w = int(WIDTH / scale)
            crop_h = int(HEIGHT / scale)
            x_start = (WIDTH - crop_w) // 2
            max_pan_y = HEIGHT - crop_h
            y_start = int(max_pan_y * t_prog)
            cropped = base_img[y_start:y_start+crop_h, x_start:x_start+crop_w]
            frame_bgr = cv2.resize(cropped, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
            
        # C. Flashlight Vignette Breathing + Scanlines via cv2.multiply SIMD
        shift_x = int(35.0 * math.sin(current_time * 0.8))
        shift_y = int(40.0 * math.cos(current_time * 0.6))
        flash_slice = BIG_FLASHLIGHT_MASK[pad + shift_y : pad + shift_y + HEIGHT, pad + shift_x : pad + shift_x + WIDTH]
        frame_bgr = cv2.multiply(frame_bgr, flash_slice, scale=1.0/200.0)
        
        # D. Subtle 2px Chromatic Aberration
        frame_bgr = apply_chromatic_aberration(frame_bgr, shift=2)
        
        # E. UI Overlays (Zero Permanent Headlines)
        
        # 1. Opening Hook UI (t < 8.5s)
        if active_scene.get("type") == "hook":
            hook_title_patch.blit(frame_bgr)
            sec_left = max(1, min(5, 5 - int(current_time)))
            cd_patch = countdown_patches.get(sec_left)
            if cd_patch is not None:
                cd_patch.blit(frame_bgr)
                
        # 2. Dynamic 3-Second Room Title Flash (Center-top, then fades out completely)
        current_opt_idx = active_scene.get("option_index")
        if current_opt_idx in room_flashes:
            rf = room_flashes[current_opt_idx]
            dt = current_time - rf["start_time"]
            if 0.0 <= dt <= 3.0:
                # Fade out during last 0.6s (2.4s to 3.0s)
                alpha_scale = 1.0 if dt < 2.4 else max(0.0, (3.0 - dt) / 0.6)
                rf["patch"].blit(frame_bgr, alpha_scale=alpha_scale)
                
        # 3. Clean Arial 58px Lower-Third Captions at y=1520px
        while caption_idx < num_captions and caption_chunks[caption_idx]["end"] < current_time:
            caption_idx += 1
            
        if caption_idx < num_captions:
            cand = caption_chunks[caption_idx]
            if cand["start"] <= current_time <= cand["end"]:
                caption_patches[caption_idx].blit(frame_bgr)
                
        # F. Stream raw BGR24 frame to FFmpeg stdin
        try:
            pipe.stdin.write(frame_bgr.tobytes())
        except (BrokenPipeError, OSError) as e:
            print(f"[RENDER] FFmpeg pipe error at frame {f}: {e}")
            break
            
        if f % 300 == 0 or f == total_frames - 1:
            progress = (f + 1) / total_frames * 100
            elapsed = time.time() - start_time
            fps_actual = (f + 1) / max(0.01, elapsed)
            eta_sec = (total_frames - (f + 1)) / max(0.01, fps_actual)
            print(f"[RENDER] Frame {f+1}/{total_frames} ({progress:.1f}%) | {fps_actual:.1f} FPS | ETA: {eta_sec:.0f}s")
            
    pipe.stdin.close()
    pipe.wait()
    total_time = time.time() - start_time
    print(f"[RENDER] Finished {total_frames} frames in {total_time:.1f}s ({total_frames/total_time:.1f} FPS)!")
    print(f"[RENDER] Output saved to: {output_mp4_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    queue_path = os.path.abspath(os.path.join(current_dir, "..", "data", "queue.json"))
    timeline_path = os.path.abspath(os.path.join(current_dir, "..", "data", "timeline.json"))
    scenes_dir = os.path.abspath(os.path.join(current_dir, "..", "assets", "ai_scenes"))
    master_audio = os.path.abspath(os.path.join(current_dir, "..", "output", "master_audio.wav"))
    output_video = os.path.abspath(os.path.join(current_dir, "..", "output", "liminal_doors_ep01.mp4"))
    
    with open(queue_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)["queue"][0]
        
    with open(timeline_path, "r", encoding="utf-8") as f:
        tl_data = json.load(f)
        timeline = tl_data["timeline"]
        caption_chunks = tl_data["captions"]
        
    build_video_frames(
        script_data=script_data,
        timeline=timeline,
        caption_chunks=caption_chunks,
        scenes_dir=scenes_dir,
        master_audio_path=master_audio,
        output_mp4_path=output_video
    )
