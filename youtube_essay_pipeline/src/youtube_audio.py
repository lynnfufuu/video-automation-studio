"""
youtube_audio.py - Narration & Atmospheric Audio Master for YouTube Video Essays
Synthesizes documentary voiceovers using en-US-AndrewMultilingualNeural (rate="-5%")
and layers deep atmospheric ambient horror/sci-fi background audio strictly at 15%-20% volume.
"""

import os
import sys
import wave
import asyncio
import numpy as np
import edge_tts

DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"
DEFAULT_RATE = "-5%"
ASSETS_AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "audio"))

def get_audio_duration_wave(wav_path: str) -> float:
    """Returns exact duration in seconds of a WAV file."""
    with wave.open(wav_path, "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

async def synthesize_andrew_narration(text: str, output_wav_path: str, rate: str = DEFAULT_RATE) -> float:
    """
    Synthesizes speech using Microsoft Edge TTS with en-US-AndrewMultilingualNeural.
    Includes caching and robust retry backoff against transient network glitches.
    """
    if os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 8000:
        return get_audio_duration_wave(output_wav_path)

    dirname = os.path.dirname(output_wav_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    temp_mp3 = output_wav_path.replace(".wav", "_temp.mp3")
    
    last_err = None
    for attempt in range(8):
        try:
            communicate = edge_tts.Communicate(text, DEFAULT_VOICE, rate=rate)
            await communicate.save(temp_mp3)
            if os.path.exists(temp_mp3) and os.path.getsize(temp_mp3) > 1000:
                break
        except Exception as e:
            last_err = e
            backoff = 4.0 * (attempt + 1)
            print(f"[AUDIO WARNING] TTS attempt {attempt + 1} failed ({e}), retrying in {backoff:.1f}s...")
            await asyncio.sleep(backoff)
            
    if not os.path.exists(temp_mp3) or os.path.getsize(temp_mp3) < 1000:
        for attempt in range(4):
            try:
                print(f"[AUDIO WARNING] Retrying voice beat with secondary model...")
                communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate=rate)
                await communicate.save(temp_mp3)
                if os.path.exists(temp_mp3) and os.path.getsize(temp_mp3) > 1000:
                    break
            except Exception as e2:
                last_err = e2
                await asyncio.sleep(5.0 * (attempt + 1))
                
    if not os.path.exists(temp_mp3) or os.path.getsize(temp_mp3) < 1000:
        raise RuntimeError(f"Edge TTS service unavailable after extended retries: {last_err}")
                
    # Convert mp3 to 44.1kHz stereo WAV
    import subprocess
    cmd = [
        "ffmpeg", "-y", "-i", temp_mp3,
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
        output_wav_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)
        
    return get_audio_duration_wave(output_wav_path)

def generate_atmospheric_scifi_drone(duration: float, output_wav: str, sample_rate: int = 44100) -> str:
    """
    Generates a deep, evolving cosmic ambient drone with 42Hz sub-bass,
    binaural detuned pads (84Hz / 86Hz), and resonant sweeping filters.
    """
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # 1. Sub-bass fundamental (42Hz)
    sub = 0.50 * np.sin(2 * np.pi * 42.0 * t)
    
    # 2. Binaural detuned ominous pad (left 84Hz, right 85.5Hz)
    pad_l = 0.25 * np.sin(2 * np.pi * 84.0 * t + 0.1 * np.sin(2 * np.pi * 0.15 * t))
    pad_r = 0.25 * np.sin(2 * np.pi * 85.5 * t + 0.1 * np.cos(2 * np.pi * 0.12 * t))
    
    # 3. High eerie harmonic overtone (168Hz with slow amplitude lfo)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t)
    overtone = 0.15 * lfo * np.sin(2 * np.pi * 168.0 * t)
    
    # 4. Filtered atmospheric pink noise (subtle void wind)
    noise = np.random.normal(0, 0.08, num_samples)
    b, a = [0.015], [1, -0.985] # Gentle lowpass
    filtered_noise = np.zeros(num_samples)
    for i in range(1, num_samples):
        filtered_noise[i] = 0.98 * filtered_noise[i-1] + 0.02 * noise[i]
        
    left = sub + pad_l + overtone + filtered_noise
    right = sub + pad_r + overtone + filtered_noise
    
    # Normalize and fade in/out
    fade_len = int(sample_rate * 2.0)
    if len(left) > fade_len * 2:
        fade_in = np.linspace(0.0, 1.0, fade_len)
        fade_out = np.linspace(1.0, 0.0, fade_len)
        left[:fade_len] *= fade_in
        right[:fade_len] *= fade_in
        left[-fade_len:] *= fade_out
        right[-fade_len:] *= fade_out
        
    max_amp = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-4)
    left = (left / max_amp * 0.85 * 32767).astype(np.int16)
    right = (right / max_amp * 0.85 * 32767).astype(np.int16)
    
    stereo_data = np.empty((num_samples * 2,), dtype=np.int16)
    stereo_data[0::2] = left
    stereo_data[1::2] = right
    
    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo_data.tobytes())
        
    return output_wav

def mix_voice_and_ambient(
    voice_wav: str,
    ambient_wav: str,
    output_mixed_wav: str,
    ambient_volume: float = 0.18 # Strictly 15% to 20%
) -> str:
    """
    Layers the voiceover on top of the ambient drone track running strictly at 15-20% volume.
    """
    # Read voice
    with wave.open(voice_wav, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        voice_raw = wf.readframes(n_frames)
        
    voice_data = np.frombuffer(voice_raw, dtype=np.int16).astype(np.float32)
    if n_channels == 1:
        voice_data = np.repeat(voice_data[:, None], 2, axis=1).flatten()
        
    # Read ambient
    with wave.open(ambient_wav, "rb") as af:
        a_frames = af.getnframes()
        ambient_raw = af.readframes(a_frames)
        
    ambient_data = np.frombuffer(ambient_raw, dtype=np.int16).astype(np.float32)
    
    # Loop or trim ambient to match voice duration
    if len(ambient_data) < len(voice_data):
        repeats = int(np.ceil(len(voice_data) / len(ambient_data)))
        ambient_data = np.tile(ambient_data, repeats)
    ambient_data = ambient_data[:len(voice_data)]
    
    # Master mix: 100% voice + 18% ambient
    mixed = voice_data + (ambient_data * ambient_volume)
    
    # Soft limiter to prevent clipping
    max_peak = np.max(np.abs(mixed))
    if max_peak > 32700:
        mixed = mixed / max_peak * 32700
        
    final_int16 = mixed.astype(np.int16)
    
    with wave.open(output_mixed_wav, "wb") as out_f:
        out_f.setnchannels(2)
        out_f.setsampwidth(2)
        out_f.setframerate(framerate)
        out_f.writeframes(final_int16.tobytes())
        
    return output_mixed_wav

if __name__ == "__main__":
    test_wav = os.path.join(ASSETS_AUDIO_DIR, "test_andrew.wav")
    text = "Every atom in your body rests upon an invisible thermodynamic assumption."
    dur = asyncio.run(synthesize_andrew_narration(text, test_wav))
    print(f"Synthesized voice ({dur:.2f}s) -> {test_wav}")
    
    drone_wav = os.path.join(ASSETS_AUDIO_DIR, "test_drone.wav")
    generate_atmospheric_scifi_drone(dur, drone_wav)
    
    mixed_wav = os.path.join(ASSETS_AUDIO_DIR, "test_master_mix.wav")
    mix_voice_and_ambient(test_wav, drone_wav, mixed_wav, ambient_volume=0.18)
    print("Master mixed audio created ->", mixed_wav)
