"""
compositor.py - High-Frequency Multi-Still 4:3 Analog Compositor (v8.0)
- True 4:3 Edge-to-Edge Full-Screen Video (1440x1080) with ZERO black borders / zero letterboxing
- ZERO room titles, ZERO headers, ZERO floating pills: 100% clean upper screen
- High-Frequency Multi-Still Scene Cuts (Wide establishing -> Corridor/Corner -> Escalating Close-up)
- 2.5D Parallax Walk-In Zoom (1.0x -> 1.15x) + Camcorder Drift per still
- Clean Smaller Italic Yellow Captions (#FFE600, 80% opacity, ZERO stroke) aligned bottom-middle
- Authentic 12% Film Grain Overlay (-vf "noise=alls=12:allf=t+u,format=yuv420p")
- Target File Size: 25.0MB - 50.0MB | Target Duration: 120s - 210s
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

CANVAS_W = 1440
CANVAS_H = 1080  # Exact 4:3 Aspect Ratio (1440 / 1080 = 4 / 3)
FPS = 30

def get_pil_font(font_path: str, size: int):
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def precompute_vignette_mask(w: int = CANVAS_W, h: int = CANVAS_H) -> np.ndarray:
    """Precomputes a subtle 4:3 flashlight vignette breathing mask."""
    cy, cx = h / 2.0, w / 2.0
    radius = math.hypot(cx, cy) * 0.95
    y, x = np.ogrid[:h, :w]
    dist_sq = (x - cx)**2 + (y - cy)**2
    mask = 1.04 - 0.28 * np.clip(dist_sq / (radius**2), 0.0, 1.0)
    mask_u8 = np.clip(mask * 200.0, 0, 255).astype(np.uint8)
    return np.dstack([mask_u8, mask_u8, mask_u8])

VIGNETTE_MASK = precompute_vignette_mask(CANVAS_W, CANVAS_H)

def apply_chromatic_aberration(bgr: np.ndarray, shift: int = 2) -> np.ndarray:
    """Subtle 2px edge chromatic aberration."""
    out = bgr.copy()
    out[:, shift:, 0] = bgr[:, :-shift, 0]   # Blue right
    out[:, :-shift, 2] = bgr[:, shift:, 2]   # Red left
    return out

class PreRenderedPatch:
    """Tightly cropped RGBA patch with float alpha blending."""
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
        if self.empty:
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

def pre_render_italic_yellow_caption(text: str, font_italic: ImageFont.ImageFont) -> PreRenderedPatch:
    """
    Renders clean, smaller Italic Yellow text (#FFE600) with ZERO outline / ZERO stroke,
    set to 80% opacity, aligned strictly to the bottom-middle of the 1440x1080 frame.
    """
    img = Image.new("RGBA", (CANVAS_W, 220), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Yellow #FFE600 at 80% opacity: (255, 230, 0, 204)
    caption_color = (255, 230, 0, 204)
    
    max_line_w = 1200
    words = text.split()
    lines = []
    cur_line = []
    for w in words:
        test_line = " ".join(cur_line + [w])
        bbox = draw.textbbox((0, 0), test_line, font=font_italic)
        if bbox[2] - bbox[0] <= max_line_w:
            cur_line.append(w)
        else:
            if cur_line:
                lines.append(" ".join(cur_line))
            cur_line = [w]
    if cur_line:
        lines.append(" ".join(cur_line))
        
    line_h = 42
    total_h = len(lines) * line_h
    start_y = (220 - total_h) // 2
    
    for idx, l in enumerate(lines):
        bbox = draw.textbbox((0, 0), l, font=font_italic)
        lw = bbox[2] - bbox[0]
        lx = (CANVAS_W - lw) // 2
        ly = start_y + idx * line_h
        # Zero stroke, zero outline, pure italic yellow at 80% opacity
        draw.text((lx, ly), l, font=font_italic, fill=caption_color)
        
    return PreRenderedPatch(img, 0, 840)

def render_master_analog_video(
    timeline_path: str,
    master_audio_path: str,
    assets_scenes_dir: str,
    output_mp4_path: str
):
    print("=" * 70)
    print("[COMPOSITOR v8.0] Starting Full 4:3 Edge-to-Edge Analog Production")
    print(f"Canvas: {CANVAS_W}x{CANVAS_H} (4:3) | ZERO UI Headers | High-Frequency Stills")
    print("=" * 70)
    
    with open(timeline_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    timeline = meta["timeline"]
    captions = meta.get("captions", [])
    total_duration = meta.get("total_duration", 198.95)
    total_frames = int(total_duration * FPS)
    
    print(f"[COMPOSITOR v8.0] Timeline: {len(timeline)} scenes | Total duration: {total_duration:.2f}s ({total_frames} frames)")
    
    # 1. Load and upsample all multi-still images to 1476x1107 (subtle 2.5% buffer for smooth crawl & drift)
    loaded_stills = {}
    LARGER_W, LARGER_H = 1476, 1107  # Exactly 2.5% buffer, zero pre-crop zoom distortion
    
    for item in timeline:
        sc_id = item["scene_id"]
        stills = item.get("stills", [
            {"still_id": f"{sc_id}_angle1"},
            {"still_id": f"{sc_id}_angle2"},
            {"still_id": f"{sc_id}_angle3"}
        ])
        
        for s in stills:
            sid = s["still_id"]
            img_p = os.path.join(assets_scenes_dir, f"{sid}.jpg")
            if not os.path.exists(img_p):
                # Fallback to base scene image if specific angle file not found
                img_p = os.path.join(assets_scenes_dir, f"{sc_id}.jpg")
                
            if sid not in loaded_stills:
                if os.path.exists(img_p):
                    img_cv = cv2.imread(img_p)
                    if img_cv is not None:
                        loaded_stills[sid] = cv2.resize(img_cv, (LARGER_W, LARGER_H), interpolation=cv2.INTER_LANCZOS4)
                if sid not in loaded_stills:
                    # Deep dark moody analog fallback
                    loaded_stills[sid] = np.full((LARGER_H, LARGER_W, 3), 16, dtype=np.uint8)
                    
    print(f"[COMPOSITOR v8.0] Loaded {len(loaded_stills)} high-resolution 4:3 camera plates.")
    
    # 2. Smaller Italic Yellow Captions (#FFE600, 80% opacity, ZERO stroke)
    font_italic = get_pil_font("C:\\Windows\\Fonts\\arialbi.ttf", 30)  # Smaller, cleaner 30px Arial Bold Italic
    print(f"[COMPOSITOR v8.0] Pre-rendering {len(captions)} natural sentence Italic Yellow captions...")
    caption_patches = [pre_render_italic_yellow_caption(c["text"], font_italic) for c in captions]
    
    # 3. Launch FFmpeg with authentic 12% film grain overlay and calibrated bitrate
    os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{CANVAS_W}x{CANVAS_H}",
        "-pix_fmt", "bgr24",
        "-r", str(FPS),
        "-i", "-",  # Video from stdin pipe
        "-i", master_audio_path,
        "-vf", "noise=alls=12:allf=t+u,format=yuv420p", # Authentic 12% film grain overlay
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
    num_captions = len(captions)
    start_time = time.time()
    
    for f in range(total_frames):
        current_time = f / float(FPS)
        
        # Identify active scene
        active_scene = timeline[-1]
        for sc in timeline:
            if sc["start_time"] <= current_time < sc["end_time"]:
                active_scene = sc
                break
                
        sc_start = active_scene["start_time"]
        sc_dur = max(0.1, active_scene["total_duration"])
        dt_scene = max(0.0, current_time - sc_start)
        
        # High-Frequency Multi-Still Angle Cycling
        stills = active_scene.get("stills", [
            {"still_id": f"{active_scene['scene_id']}_angle1"},
            {"still_id": f"{active_scene['scene_id']}_angle2"},
            {"still_id": f"{active_scene['scene_id']}_angle3"}
        ])
        num_stills = max(1, len(stills))
        still_duration = sc_dur / num_stills
        current_still_idx = min(num_stills - 1, int(dt_scene / still_duration))
        active_still_id = stills[current_still_idx]["still_id"]
        
        # Progress within this specific still (0.0 -> 1.0)
        still_progress = (dt_scene - current_still_idx * still_duration) / max(0.05, still_duration)
        still_progress = min(1.0, max(0.0, still_progress))
        
        # 1. Subtle, imperceptible analog crawl (max 2.0% over the entire still)
        zoom_scale = 1.0 + 0.02 * still_progress
        
        # 2. Gentle organic handheld drift
        drift_x = math.sin(current_time * 0.35 + current_still_idx * 0.8) * 3.5
        drift_y = math.cos(current_time * 0.25 + current_still_idx * 0.6) * 2.5
        
        # Crop from 1680x1260 to CANVAS_W x CANVAS_H (1440x1080)
        crop_w = int(CANVAS_W / zoom_scale)
        crop_h = int(CANVAS_H / zoom_scale)
        
        cx = int(LARGER_W / 2.0 + drift_x)
        cy = int(LARGER_H / 2.0 + drift_y)
        
        x1 = max(0, min(LARGER_W - crop_w, cx - crop_w // 2))
        y1 = max(0, min(LARGER_H - crop_h, cy - crop_h // 2))
        
        source_frame = loaded_stills.get(active_still_id, loaded_stills[list(loaded_stills.keys())[0]])
        cropped = source_frame[y1:y1 + crop_h, x1:x1 + crop_w]
        
        # Edge-to-edge full screen 4:3 frame
        frame_4_3 = cv2.resize(cropped, (CANVAS_W, CANVAS_H), interpolation=cv2.INTER_LINEAR)
        
        # 3. Dynamic Flashlight Breathing Vignette
        b_pulse = 1.0 + 0.03 * math.sin(current_time * 2.2)
        vignette_cur = np.clip(VIGNETTE_MASK.astype(np.float32) * b_pulse, 0, 255).astype(np.uint8)
        frame_4_3 = (frame_4_3.astype(np.uint16) * vignette_cur >> 8).astype(np.uint8)
        
        # 4. Subtle CRT horizontal scanlines
        frame_4_3[1::2] = (frame_4_3[1::2].astype(np.uint16) * 248 >> 8).astype(np.uint8)
        
        # 5. Faint rolling VHS tracking scanline
        roll_y = int((current_time * 36.0) % CANVAS_H)
        y_a, y_b = max(0, roll_y - 3), min(CANVAS_H, roll_y + 3)
        frame_4_3[y_a:y_b] = (frame_4_3[y_a:y_b].astype(np.uint16) * 240 >> 8).astype(np.uint8)
        
        # 6. Quick 1-frame analog switch cut between stills
        if still_progress < 0.05 and current_still_idx > 0:
            # Subtle tape splice twitch
            frame_4_3 = np.roll(frame_4_3, 4, axis=1)
            frame_4_3[::4] = (frame_4_3[::4].astype(np.uint16) * 230 >> 8).astype(np.uint8)
            
        # 7. Subtle 2px chromatic aberration
        frame_4_3 = apply_chromatic_aberration(frame_4_3, shift=2)
        
        # 8. Clean Smaller Italic Yellow Caption at bottom-middle (ZERO stroke, 80% opacity)
        while caption_idx < num_captions and captions[caption_idx]["end"] < current_time:
            caption_idx += 1
            
        if caption_idx < num_captions:
            cand = captions[caption_idx]
            if cand["start"] <= current_time <= cand["end"]:
                caption_patches[caption_idx].blit(frame_4_3)
                
        # 9. Stream frame directly to FFmpeg stdin pipe (Edge-to-Edge full screen)
        try:
            pipe.stdin.write(frame_4_3.tobytes())
        except (BrokenPipeError, OSError) as e:
            print(f"[COMPOSITOR v8.0] FFmpeg pipe error at frame {f}: {e}")
            break
            
        if f % 300 == 0 or f == total_frames - 1:
            progress = (f + 1) / total_frames * 100
            elapsed = time.time() - start_time
            fps_actual = (f + 1) / max(0.01, elapsed)
            eta_sec = (total_frames - (f + 1)) / max(0.01, fps_actual)
            print(f"[COMPOSITOR v8.0] Frame {f+1}/{total_frames} ({progress:.1f}%) | {fps_actual:.1f} FPS | ETA: {eta_sec:.0f}s")
            
    pipe.stdin.close()
    pipe.wait()
    
    elapsed_total = time.time() - start_time
    print(f"[COMPOSITOR v8.0] Master video finished: {total_frames} frames in {elapsed_total:.1f}s ({total_frames/max(0.1, elapsed_total):.1f} FPS)")
    print(f"[COMPOSITOR v8.0] Saved to: {output_mp4_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    timeline_file = os.path.abspath(os.path.join(current_dir, "..", "data", "timeline.json"))
    master_audio_file = os.path.abspath(os.path.join(current_dir, "..", "output", "master_audio.wav"))
    assets_scenes = os.path.abspath(os.path.join(current_dir, "..", "assets", "ai_scenes"))
    final_output = os.path.abspath(os.path.join(current_dir, "..", "output", "liminal_doors_ep01.mp4"))
    
    render_master_analog_video(
        timeline_path=timeline_file,
        master_audio_path=master_audio_file,
        assets_scenes_dir=assets_scenes,
        output_mp4_path=final_output
    )
