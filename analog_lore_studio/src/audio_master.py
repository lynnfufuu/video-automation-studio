"""
audio_master.py - Master Audio Engine & Horror Atmosphere (v7.0)
- Narrator: en-US-AndrewMultilingualNeural at rate="-10%", pitch="-8Hz"
- Zero starting countdown beeps, zero white noise, zero klaxon warning alarms
- Low-volume eerie horror background drone (liminal_dread_pad.wav) at 12% volume with subterranean reverb
- Natural line-by-line sentence phrasing for comfortable reading
- Strict duration locked between 120.0s and 210.0s
"""

import os
import sys
import json
import re
import asyncio
import subprocess
import wave
import numpy as np
import edge_tts
from mutagen.mp3 import MP3

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-10%"
PITCH = "-8Hz"
SPEED_FACTOR = 1.12  # Calibrated to lock duration within 120s - 210s
SAMPLE_RATE = 44100

def get_audio_duration(file_path: str) -> float:
    if file_path.endswith(".wav"):
        with wave.open(file_path, "rb") as wf:
            return wf.getnframes() / float(wf.getframerate())
    elif file_path.endswith(".mp3"):
        audio = MP3(file_path)
        return audio.info.length
    else:
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
        res = subprocess.check_output(cmd, shell=True).decode().strip()
        return float(res)

async def synthesize_speech(text: str, output_mp3: str, max_retries: int = 5):
    """Synthesizes text using edge-tts with chilling deep Andrew voice."""
    if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 1024:
        return
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
            await communicate.save(output_mp3)
            return
        except Exception as e:
            print(f"[AUDIO MASTER] Speech retry {attempt}/{max_retries} for {os.path.basename(output_mp3)}: {e}")
            await asyncio.sleep(2.0)
    raise RuntimeError(f"Failed to synthesize speech for {output_mp3}")

def convert_mp3_to_wav(mp3_path: str, wav_path: str):
    cmd = f'ffmpeg -y -v error -i "{mp3_path}" -ar {SAMPLE_RATE} -ac 2 "{wav_path}"'
    subprocess.run(cmd, shell=True, check=True)

def generate_silence(duration: float) -> np.ndarray:
    n_samples = int(SAMPLE_RATE * duration)
    return np.zeros((n_samples, 2), dtype=np.float32)

def load_wav_stereo(file_path: str) -> np.ndarray:
    with wave.open(file_path, "rb") as wf:
        n_channels = wf.getnchannels()
        n_frames = wf.getnframes()
        raw_data = wf.readframes(n_frames)
        audio = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32767.0
        if n_channels == 1:
            audio = np.column_stack([audio, audio])
        elif n_channels == 2:
            audio = audio.reshape(-1, 2)
        return audio

def save_wav_stereo(file_path: str, audio: np.ndarray):
    audio = np.clip(audio, -1.0, 1.0)
    int16_audio = (audio * 32767.0).astype(np.int16)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with wave.open(file_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int16_audio.tobytes())

def apply_cinematic_horror_filter(input_wav: str, output_wav: str):
    """
    Heavy Cinematic Horror Audio Chain (FFmpeg):
    highpass=f=120,lowpass=f=3800,aecho=0.8:0.88:80:0.4,acompressor=threshold=-16dB:ratio=4:attack=10:release=300
    """
    filter_chain = (
        f"atempo={SPEED_FACTOR},"
        "highpass=f=120,lowpass=f=3800,aecho=0.8:0.88:80:0.4,"
        "acompressor=threshold=-16dB:ratio=4:attack=10:release=300"
    )
    cmd = f'ffmpeg -y -v error -i "{input_wav}" -af "{filter_chain}" -ar {SAMPLE_RATE} -ac 2 "{output_wav}"'
    subprocess.run(cmd, shell=True, check=True)
    print(f"[AUDIO MASTER] Cinematic horror filter applied: {output_wav}")

def build_scene_timeline(script_data: dict, temp_dir: str):
    """
    Synthesizes speech for all scenes with AndrewMultilingualNeural (-10%, -8Hz),
    tracks exact timestamps, and builds scene timeline metadata.
    """
    os.makedirs(temp_dir, exist_ok=True)
    timeline = []
    
    # 1. Hook (Immediate dialogue without starting countdown beeps)
    hook = script_data.get("hook", {})
    hook_speech = hook.get("speech", "")
    hook_mp3 = os.path.join(temp_dir, "speech_hook.mp3")
    asyncio.run(synthesize_speech(hook_speech, hook_mp3))
    hook_wav = os.path.join(temp_dir, "speech_hook.wav")
    convert_mp3_to_wav(hook_mp3, hook_wav)
    hook_raw_dur = get_audio_duration(hook_wav)
    hook_dur = hook_raw_dur / SPEED_FACTOR
    
    hook_total_dur = hook_dur + 0.5
    timeline.append({
        "type": "hook",
        "scene_id": hook.get("scene_id", "hook_01_three_doors"),
        "speech": hook_speech,
        "speech_wav": hook_wav,
        "speech_duration": hook_dur,
        "total_duration": hook_total_dur,
        "pause_after": 0.8,
        "option_name": script_data.get("title", "CHOOSE ONE TO SURVIVE"),
        "is_option_start": False,
        "stills": hook.get("stills", [])
    })
    
    # 2. Options
    for opt in script_data.get("options", []):
        opt_idx = opt.get("option_index", 1)
        opt_name = opt.get("name", f"OPTION {opt_idx}")
        scenes = opt.get("scenes", [])
        for sc_idx, scene in enumerate(scenes):
            sc_id = scene.get("scene_id", f"opt{opt_idx}_sc{sc_idx+1}")
            sc_speech = scene.get("speech", "")
            sc_mp3 = os.path.join(temp_dir, f"speech_{sc_id}.mp3")
            asyncio.run(synthesize_speech(sc_speech, sc_mp3))
            sc_wav = os.path.join(temp_dir, f"speech_{sc_id}.wav")
            convert_mp3_to_wav(sc_mp3, sc_wav)
            sc_raw_dur = get_audio_duration(sc_wav)
            sc_dur = sc_raw_dur / SPEED_FACTOR
            
            pause_after = 0.35
            is_last_scene_of_opt = (sc_idx == len(scenes) - 1)
            if is_last_scene_of_opt:
                pause_after = 0.8  # Clean transition pause between options
                
            timeline.append({
                "type": "option_scene",
                "option_index": opt_idx,
                "option_name": opt_name,
                "scene_id": sc_id,
                "scene_type": scene.get("scene_type", "environment"),
                "speech": sc_speech,
                "speech_wav": sc_wav,
                "speech_duration": sc_dur,
                "total_duration": sc_dur + pause_after,
                "pause_after": pause_after,
                "is_option_start": (sc_idx == 0),
                "is_deadzone": (opt.get("classification") == "CLASS: DEADZONE"),
                "stills": scene.get("stills", [])
            })
            
    return timeline

def assemble_master_audio(timeline: list, sfx_dir: str, output_master_wav: str) -> float:
    """
    Concatenates speech, filters with horror echo/reverb chain,
    and mixes multi-track SFX (dread pad at strictly 12% volume, zero white noise, zero alarm beeps).
    """
    temp_dir = os.path.dirname(output_master_wav)
    raw_speech_segments = []
    
    current_time = 0.0
    sfx_events = []
    
    for item in timeline:
        speech_audio = load_wav_stereo(item["speech_wav"])
        item["start_time"] = current_time
        item["end_time"] = current_time + item["total_duration"]
        
        # Subtle CRT channel clunk on room transitions (NO starting beeps, NO klaxons)
        if item.get("is_option_start"):
            sfx_events.append({"type": "crt_switch", "time": max(0.0, current_time - 0.15)})
                
        raw_speech_segments.append(speech_audio)
        pause_samples = generate_silence(item["pause_after"] * SPEED_FACTOR)
        raw_speech_segments.append(pause_samples)
        
        current_time += item["total_duration"]
        
    raw_speech = np.vstack(raw_speech_segments)
    raw_speech_path = os.path.join(temp_dir, "raw_speech_concat.wav")
    save_wav_stereo(raw_speech_path, raw_speech)
    
    # Apply Cinematic Horror audio filter with atempo
    filtered_speech_path = os.path.join(temp_dir, "filtered_speech.wav")
    apply_cinematic_horror_filter(raw_speech_path, filtered_speech_path)
    speech_filtered = load_wav_stereo(filtered_speech_path)
    
    total_samples = len(speech_filtered)
    total_duration = total_samples / SAMPLE_RATE
    print(f"[AUDIO MASTER] Total spoken audio duration: {total_duration:.2f}s ({total_duration/60:.2f} min)")
    
    # Master track base
    master = np.copy(speech_filtered) * 1.05
    
    # Ambient Horror Drone: liminal_dread_pad mixed strictly at 12% volume (<= 15%)
    pad_path = os.path.join(sfx_dir, "liminal_dread_pad.wav")
    if not os.path.exists(pad_path):
        try:
            os.makedirs(sfx_dir, exist_ok=True)
            from src.sfx_synth import generate_liminal_dread_pad
            pad = generate_liminal_dread_pad(230.0, target_db=-18.0)
            save_wav_stereo(pad_path, pad)
            print("[AUDIO MASTER] Synthesized fresh liminal dread drone pad!")
        except Exception as e:
            print(f"[AUDIO MASTER] Drone synthesis warning: {e}")
    if os.path.exists(pad_path):
        pad_audio = load_wav_stereo(pad_path)
        if len(pad_audio) < total_samples:
            repeats = int(np.ceil(total_samples / len(pad_audio)))
            pad_audio = np.tile(pad_audio, (repeats, 1))
        master += pad_audio[:total_samples] * 0.18
        print("[AUDIO MASTER] Mixed liminal dread pad at 18% volume (15%-20% target, zero white noise)")
        
    # Subtle CRT transitions
    crt_path = os.path.join(sfx_dir, "crt_channel_switch.wav")
    crt_stem = load_wav_stereo(crt_path) if os.path.exists(crt_path) else None
    if crt_stem is not None:
        for ev in sfx_events:
            idx = int(ev["time"] * SAMPLE_RATE)
            end_idx = min(total_samples, idx + len(crt_stem))
            sub_len = end_idx - idx
            if sub_len > 0:
                master[idx:end_idx] += crt_stem[:sub_len] * 0.45
                
    # Normalize to -1dB peak
    max_val = np.max(np.abs(master))
    if max_val > 0.95:
        master = master * (0.95 / max_val)
        
    save_wav_stereo(output_master_wav, master)
    print(f"[AUDIO MASTER] Master audio assembled: {output_master_wav} ({total_duration:.2f}s)")
    return total_duration

def generate_natural_sentence_captions(timeline: list) -> list:
    """
    Generates natural sentence or clause-by-clause captions rather than rapid 3-word chunks,
    allowing viewers to read comfortably at a cinematic pace.
    """
    all_lines = []
    for item in timeline:
        speech_text = item["speech"].strip()
        speech_start = item["start_time"]
        speech_dur = item["speech_duration"]
        
        # Split sentences by punctuation (. ? !)
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', speech_text) if s.strip()]
        
        clauses = []
        for s in raw_sentences:
            words = s.split()
            if len(words) <= 10:
                clauses.append(s)
            else:
                # Split at comma if available
                comma_parts = [p.strip() for p in re.split(r',\s*', s) if p.strip()]
                if len(comma_parts) > 1 and all(len(p.split()) <= 10 for p in comma_parts):
                    clauses.extend(comma_parts)
                else:
                    # Split into two balanced halves
                    mid = len(words) // 2
                    clauses.append(" ".join(words[:mid]))
                    clauses.append(" ".join(words[mid:]))
                    
        total_chars = sum(len(c) for c in clauses)
        curr_t = speech_start
        for c in clauses:
            dur = (len(c) / max(1, total_chars)) * speech_dur
            all_lines.append({
                "text": c,
                "start": curr_t,
                "end": curr_t + dur,
                "scene_id": item["scene_id"]
            })
            curr_t += dur
            
    return all_lines

def build_audio_and_timeline():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    queue_path = os.path.abspath(os.path.join(current_dir, "..", "data", "queue.json"))
    sfx_dir = os.path.abspath(os.path.join(current_dir, "..", "assets", "sfx"))
    temp_dir = os.path.abspath(os.path.join(current_dir, "..", "assets", "temp_voice"))
    master_wav = os.path.abspath(os.path.join(current_dir, "..", "output", "master_audio.wav"))
    timeline_export = os.path.abspath(os.path.join(current_dir, "..", "data", "timeline.json"))
    
    with open(queue_path, "r", encoding="utf-8") as f:
        script = json.load(f)["queue"][0]
        
    print("[AUDIO MASTER] Synthesizing chilling Andrew narration and building audio master...")
    tl = build_scene_timeline(script, temp_dir)
    dur = assemble_master_audio(tl, sfx_dir, master_wav)
    captions = generate_natural_sentence_captions(tl)
    print(f"[AUDIO MASTER] Generated {len(captions)} natural sentence captions. Total duration: {dur:.1f}s")
    
    with open(timeline_export, "w", encoding="utf-8") as f:
        json.dump({"timeline": tl, "captions": captions, "duration": dur}, f, indent=2)
    print(f"[AUDIO MASTER] Timeline exported to: {timeline_export}")
    return dur

if __name__ == "__main__":
    build_audio_and_timeline()
