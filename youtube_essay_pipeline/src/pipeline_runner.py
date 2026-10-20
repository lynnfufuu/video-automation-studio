"""
pipeline_runner.py - End-to-End Master Pipeline Runner for YouTube Video Essays
Orchestrates:
1. Long-form multi-chapter script loading / generation
2. Sentence-by-sentence Andrew voiceover synthesis (rate="-5%")
3. High-definition FLUX cinematic visual asset generation for every beat
4. Chapter transition title card creation
5. Deep atmospheric sci-fi/horror ambient track layering (strictly at 18% volume)
6. Synced lower-third italic yellow captions and Ken Burns rendering
7. Final MP4 export to ./youtube_essay_pipeline/output/
"""

import os
import sys
import json
import time
import asyncio
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add local src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youtube_script import YouTubeEssayScriptEngine
from youtube_flux import generate_flux_image
from youtube_audio import synthesize_andrew_narration, generate_atmospheric_scifi_drone, mix_voice_and_ambient
from youtube_assembler import create_chapter_title_card, split_into_caption_phrases, render_cinematic_essay_sequence

PIPELINE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(PIPELINE_ROOT, "output")
ASSETS_DIR = os.path.join(PIPELINE_ROOT, "assets")

async def build_youtube_essay_episode(topic_key: str = "false_vacuum_decay") -> str:
    print("=" * 80)
    print("🎬 [YOUTUBE ESSAY PIPELINE] Launching Documentary Production Run")
    print("Aesthetic: Dark science / cosmic horror video essay (Stickman Explains / Judicium)")
    print("Voice: en-US-AndrewMultilingualNeural (rate: -5%) | Ambient: 18% Dark Drone")
    print("Format: 16:9 Widescreen (1920x1080) | Lower-Third Subtitles (#FFE600 80% opacity)")
    print("=" * 80)
    
    script_engine = YouTubeEssayScriptEngine()
    script = script_engine.get_essay_script(topic_key)
    
    title = script["title"]
    chapters = script["chapters"]
    
    print(f"\n[TOPIC] '{title}' ({len(chapters)} Chapters)")
    
    episode_dir = os.path.join(ASSETS_DIR, "episodes", topic_key)
    os.makedirs(episode_dir, exist_ok=True)
    
    timeline_beats = []
    all_captions = []
    speech_wav_paths = []
    current_time = 0.0
    
    # 0. Process Opening Intro Hook & Welcome (if present)
    if "intro_hook" in script and "beats" in script["intro_hook"]:
        intro_beats = script["intro_hook"]["beats"]
        print("\n" + "-" * 75)
        print(f"🎬 [OPENING HOOK & CHANNEL INTRO] ({len(intro_beats)} visual beats)")
        print("-" * 75)
        for b_idx, beat in enumerate(intro_beats):
            beat_id = beat["beat_id"]
            speech_text = beat["speech"]
            prompt = beat["visual_prompt"]
            print(f"  [Intro Beat {b_idx+1:02d}/{len(intro_beats):02d}] '{speech_text[:50]}...'")
            
            voice_path = os.path.join(episode_dir, f"{beat_id}_voice.wav")
            dur = await synthesize_andrew_narration(speech_text, voice_path, rate="-5%")
            speech_wav_paths.append(voice_path)
            
            still_path = os.path.join(episode_dir, f"{beat_id}_flux.jpg")
            generate_flux_image(prompt, still_path, seed=50 + b_idx)
            
            beat_dur = dur
            timeline_beats.append({
                "beat_id": beat_id,
                "image_path": still_path,
                "start_time": current_time,
                "end_time": current_time + beat_dur,
                "duration": beat_dur
            })
            captions = split_into_caption_phrases(speech_text, current_time, dur, max_words=5)
            all_captions.extend(captions)
            current_time += beat_dur

    # Process each chapter
    for ch_idx, chapter in enumerate(chapters):
        ch_num = chapter.get("chapter_index", ch_idx + 1)
        ch_title = chapter.get("chapter_title", f"Part {ch_num}")
        beats = chapter.get("beats", [])
        
        print("\n" + "-" * 75)
        print(f"📘 [CHAPTER {ch_num}] {ch_title} ({len(beats)} visual beats)")
        print("-" * 75)
        
        # 1. Chapter Title Card Beat (2.8 seconds atmospheric intro)
        title_card_img = os.path.join(episode_dir, f"ch_{ch_num:02d}_titlecard.jpg")
        create_chapter_title_card(ch_num, ch_title, title_card_img)
        
        title_card_dur = 2.8
        # Create silent audio spacer for title card
        title_spacer_wav = os.path.join(episode_dir, f"ch_{ch_num:02d}_spacer.wav")
        if not os.path.exists(title_spacer_wav):
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                "-t", str(title_card_dur), title_spacer_wav
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        speech_wav_paths.append(title_spacer_wav)
        
        timeline_beats.append({
            "beat_id": f"ch_{ch_num:02d}_title",
            "image_path": title_card_img,
            "start_time": current_time,
            "end_time": current_time + title_card_dur,
            "duration": title_card_dur
        })
        current_time += title_card_dur
        
        # 2. Process sentence beats
        for b_idx, beat in enumerate(beats):
            beat_id = beat["beat_id"]
            speech_text = beat["speech"]
            prompt = beat["visual_prompt"]
            
            print(f"  [Beat {b_idx+1:02d}/{len(beats):02d}] '{speech_text[:50]}...'")
            
            # Synthesize Andrew Multilingual Narration (-5% rate)
            voice_path = os.path.join(episode_dir, f"{beat_id}_voice.wav")
            dur = await synthesize_andrew_narration(speech_text, voice_path, rate="-5%")
            speech_wav_paths.append(voice_path)
            
            # Generate FLUX Cinematic Still (1920x1080)
            still_path = os.path.join(episode_dir, f"{beat_id}_flux.jpg")
            generate_flux_image(prompt, still_path, seed=100 + ch_num * 50 + b_idx)
            
            # Beat duration locked directly to exact audio duration
            beat_dur = dur
            timeline_beats.append({
                "beat_id": beat_id,
                "image_path": still_path,
                "start_time": current_time,
                "end_time": current_time + beat_dur,
                "duration": beat_dur
            })
            
            # Lower-third captions: small, italic yellow, 80% opacity, 1 phrase at a time
            captions = split_into_caption_phrases(speech_text, current_time, dur, max_words=5)
            all_captions.extend(captions)
            
            current_time += beat_dur

    # 3. Concatenate all voice segments
    print("\n[AUDIO MASTER] Concatenating narrative voice track...")
    concat_list = os.path.join(episode_dir, "speech_concat_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for wp in speech_wav_paths:
            f.write(f"file '{wp.replace(os.sep, '/')}'\n")
            
    concat_speech = os.path.join(episode_dir, "master_speech.wav")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c", "copy", concat_speech
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 4. Generate & Layer 18% Atmospheric Ambient Drone
    print(f"[AUDIO MASTER] Synthesizing cosmic ambient drone ({current_time:.1f}s)...")
    drone_wav = os.path.join(episode_dir, "ambient_drone.wav")
    generate_atmospheric_scifi_drone(current_time, drone_wav)
    
    master_audio = os.path.join(episode_dir, "master_soundtrack.wav")
    mix_voice_and_ambient(
        voice_wav=concat_speech,
        ambient_wav=drone_wav,
        output_mixed_wav=master_audio,
        ambient_volume=0.18 # Strictly 15% to 20%
    )
    
    # 5. Assemble Video (Ken Burns + Title Cards + Lower-Third Captions)
    output_mp4 = os.path.join(OUTPUT_DIR, f"youtube_essay_{topic_key}.mp4")
    # Calibrated for 8-10 mins (480-600s) -> 100-120 MB:
    # 1500k video + 160k audio = 1660k total => ~108 MB for 540s
    render_cinematic_essay_sequence(
        timeline_beats=timeline_beats,
        captions=all_captions,
        master_audio_path=master_audio,
        output_mp4_path=output_mp4,
        total_duration=current_time,
        video_bitrate="1500k"
    )
    
    print("\n" + "=" * 80)
    print(f"🎉 [EPISODE READY] Output successfully exported -> {output_mp4}")
    print("=" * 80)
    
    # Telegram Push Notification (if configured)
    try:
        from bot.notifier import send_telegram_message
        size_mb = os.path.getsize(output_mp4) / 1024 / 1024
        send_telegram_message(
            f"🎉 *YouTube Video Essay Rendered!*\n"
            f"• *Title:* {title}\n"
            f"• *Duration:* {current_time/60:.2f} mins ({current_time:.1f}s)\n"
            f"• *Size:* {size_mb:.1f} MB\n"
            f"• *File:* `{os.path.basename(output_mp4)}`"
        )
    except Exception:
        pass
        
    return output_mp4

if __name__ == "__main__":
    target_topic = sys.argv[1] if len(sys.argv) > 1 else "japanese_urban_legends"
    asyncio.run(build_youtube_essay_episode(target_topic))
