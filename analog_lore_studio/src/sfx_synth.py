"""
sfx_synth.py - Multi-Track Procedural Horror Soundscape Synthesizer
Vectorized with NumPy for instant generation (<2 seconds total).
Generates creepy ambient horror drone with deep subterranean reverb echo.
Zero white noise.
"""

import os
import wave
import numpy as np

SAMPLE_RATE = 44100

def save_wav_stereo(filename: str, audio_stereo: np.ndarray, sample_rate: int = SAMPLE_RATE):
    """Saves a (N, 2) numpy float array (-1.0 to 1.0) as 16-bit stereo WAV."""
    audio_stereo = np.clip(audio_stereo, -1.0, 1.0)
    int16_audio = (audio_stereo * 32767.0).astype(np.int16)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16_audio.tobytes())
    print(f"[SFX] Generated: {filename} ({len(audio_stereo)/sample_rate:.1f}s)")

def db_to_linear(db: float) -> float:
    return 10.0 ** (db / 20.0)

def apply_subterranean_reverb(stereo: np.ndarray, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Simulates a vast, pitch-black subterranean cavern with damped multi-tap echoes."""
    out = stereo.copy()
    n_samples = len(stereo)
    
    # Cavern reflection delays and decays
    delays_sec = [0.065, 0.140, 0.230, 0.380, 0.540, 0.720, 1.050]
    gains = [0.45, 0.35, 0.28, 0.22, 0.16, 0.11, 0.07]
    
    for d, g in zip(delays_sec, gains):
        delay_pts = int(d * sample_rate)
        if delay_pts < n_samples:
            # Damped echo
            echo_l = np.roll(stereo[:, 0], delay_pts) * g
            echo_r = np.roll(stereo[:, 1], delay_pts) * g
            echo_l[:delay_pts] = 0
            echo_r[:delay_pts] = 0
            
            # Cross-stereo reflections
            out[:, 0] += echo_r * 0.4 + echo_l * 0.6
            out[:, 1] += echo_l * 0.4 + echo_r * 0.6
            
    return out

def generate_liminal_dread_pad(duration: float = 230.0, target_db: float = -18.0) -> np.ndarray:
    """Evolving dark cinematic sub-bass drone + eerie minor-chord atmospheric swells with subterranean cavern reverb."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    
    # 1. Dark sub-bass drone (fundamental ~43.65 Hz [F1], detuned oscillators)
    f0 = 43.65
    sub1 = np.sin(2 * np.pi * f0 * t)
    sub2 = 0.75 * np.sin(2 * np.pi * (f0 * 1.004) * t + 0.4)
    sub3 = 0.45 * np.sin(2 * np.pi * (f0 * 0.5) * t)
    drone = sub1 + sub2 + sub3
    
    # 2. Atmospheric minor pad swells (F minor / C minor eerie notes)
    pad = np.zeros(n_samples)
    pad_notes = [87.3, 103.8, 130.8, 155.6]
    for freq in pad_notes:
        detune = freq * (1.0 + 0.003 * np.sin(2 * np.pi * 0.15 * t))
        tone = np.sin(2 * np.pi * detune * t)
        pad += tone * 0.25
        
    # Evolving swell envelope: slow undulating breathing swell every 18 seconds
    swell_env = 0.35 + 0.65 * (0.5 * (1.0 + np.sin(2 * np.pi * (1.0 / 18.0) * t - np.pi / 2)))
    pad *= swell_env
    
    delay_samples = int(SAMPLE_RATE * 0.015)
    pad_l = pad
    pad_r = np.roll(pad, delay_samples)
    
    drone_l = drone * (0.9 + 0.1 * np.sin(2 * np.pi * 0.08 * t))
    drone_r = drone * (0.9 - 0.1 * np.sin(2 * np.pi * 0.08 * t))
    
    combined_l = drone_l * 0.7 + pad_l * 0.5
    combined_r = drone_r * 0.7 + pad_r * 0.5
    stereo = np.column_stack([combined_l, combined_r])
    
    # Apply deep subterranean cavern reverb echo
    stereo = apply_subterranean_reverb(stereo, SAMPLE_RATE)
    
    # Gentle analog saturation
    stereo = np.tanh(stereo * 1.2)
    
    # Normalize to target RMS
    rms = np.sqrt(np.mean(stereo ** 2))
    target_rms = db_to_linear(target_db)
    stereo = stereo * (target_rms / (rms + 1e-9))
    return stereo

def generate_crt_channel_switch(duration: float = 0.6) -> np.ndarray:
    """Heavy analog TV static burst + mechanical VCR clunk for transitions."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    
    static = np.random.normal(0, 1, n_samples) * np.exp(-t * 6.0)
    thud = np.sin(2 * np.pi * 85.0 * t) * np.exp(-t * 22.0)
    snap = np.sin(2 * np.pi * 240.0 * t) * np.exp(-t * 45.0)
    clunk = (thud * 0.8 + snap * 0.4)
    
    combined_l = static * 0.6 + clunk * 0.7
    combined_r = static * 0.6 + clunk * 0.7
    stereo = np.column_stack([combined_l, combined_r])
    return np.clip(stereo, -1.0, 1.0)

def generate_clock_countdown(duration: float = 8.0) -> np.ndarray:
    """Slow, echoed metallic clock ticks for the opening choice hook."""
    n_samples = int(SAMPLE_RATE * duration)
    stereo = np.zeros((n_samples, 2))
    
    tick_times = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    for tick_t in tick_times:
        start_idx = int(tick_t * SAMPLE_RATE)
        tick_len = int(SAMPLE_RATE * 0.45)
        if start_idx + tick_len > n_samples:
            continue
        tt = np.linspace(0, 0.45, tick_len, endpoint=False)
        ping1 = np.sin(2 * np.pi * 1850.0 * tt) * np.exp(-tt * 35.0)
        ping2 = np.sin(2 * np.pi * 2420.0 * tt) * np.exp(-tt * 45.0) * 0.6
        body = np.sin(2 * np.pi * 320.0 * tt) * np.exp(-tt * 20.0) * 0.4
        single_tick = ping1 + ping2 + body
        
        stereo[start_idx:start_idx+tick_len, 0] += single_tick * 0.75
        stereo[start_idx:start_idx+tick_len, 1] += single_tick * 0.75
        
        echo1_idx = start_idx + int(SAMPLE_RATE * 0.12)
        if echo1_idx + tick_len <= n_samples:
            stereo[echo1_idx:echo1_idx+tick_len, 0] += single_tick * 0.35
            stereo[echo1_idx:echo1_idx+tick_len, 1] += single_tick * 0.15
            
        echo2_idx = start_idx + int(SAMPLE_RATE * 0.24)
        if echo2_idx + tick_len <= n_samples:
            stereo[echo2_idx:echo2_idx+tick_len, 0] += single_tick * 0.12
            stereo[echo2_idx:echo2_idx+tick_len, 1] += single_tick * 0.25

    return np.clip(stereo, -1.0, 1.0)

def generate_eas_danger_tone(duration: float = 1.8) -> np.ndarray:
    """Vintage unsettling Emergency Alert System dual-tone chime (853 Hz + 960 Hz)."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    
    tone1 = np.sin(2 * np.pi * 853.0 * t)
    tone2 = np.sin(2 * np.pi * 960.0 * t)
    raw = (tone1 + tone2) * 0.45
    
    attack_samples = int(SAMPLE_RATE * 0.04)
    release_samples = int(SAMPLE_RATE * 0.3)
    env = np.ones(n_samples)
    env[:attack_samples] = np.linspace(0, 1, attack_samples)
    env[-release_samples:] = np.linspace(1, 0, release_samples)
    
    raw = np.tanh(raw * env * 1.3) * 0.8
    stereo = np.column_stack([raw, raw])
    return stereo

def build_all_sfx(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[SFX] Synthesizing horror soundscape stems (No White Noise) in {output_dir}...")
    
    pad = generate_liminal_dread_pad(230.0, target_db=-18.0)
    save_wav_stereo(os.path.join(output_dir, "liminal_dread_pad.wav"), pad)
    
    crt = generate_crt_channel_switch(0.6)
    save_wav_stereo(os.path.join(output_dir, "crt_channel_switch.wav"), crt)
    
    clock = generate_clock_countdown(8.0)
    save_wav_stereo(os.path.join(output_dir, "clock_countdown.wav"), clock)
    
    eas = generate_eas_danger_tone(1.8)
    save_wav_stereo(os.path.join(output_dir, "eas_danger_tone.wav"), eas)
    
    print("[SFX] Horror soundscape stems generated successfully!")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(current_dir, "..", "assets", "sfx"))
    build_all_sfx(assets_dir)
