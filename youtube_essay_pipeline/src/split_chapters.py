import json
import os
import subprocess

def get_dur(p):
    out = subprocess.check_output([
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        p
    ]).decode().strip()
    return float(out)

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script_path = os.path.join(root, "data", "japanese_urban_legends.json")
    ep_dir = os.path.join(root, "assets", "episodes", "japanese_urban_legends")
    output_dir = os.path.join(root, "output", "chapters")
    os.makedirs(output_dir, exist_ok=True)
    master_video = os.path.join(root, "output", "youtube_essay_japanese_urban_legends.mp4")

    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    current_time = 0.0
    intro_start = current_time
    for b in data.get("intro_hook", {}).get("beats", []):
        wp = os.path.join(ep_dir, f"{b['beat_id']}_voice.wav")
        current_time += get_dur(wp)
    intro_end = current_time

    print(f"Intro: {intro_start:.2f}s to {intro_end:.2f}s ({intro_end - intro_start:.2f}s)")

    # Slice intro
    intro_out = os.path.join(output_dir, "00_intro_hook.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-ss", f"{intro_start:.2f}", "-to", f"{intro_end:.2f}",
        "-i", master_video, "-c", "copy", intro_out
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Created: {intro_out}")

    for ch in data.get("chapters", []):
        ch_idx = ch["chapter_index"]
        ch_name = ch["chapter_title"].split(":")[0].strip().replace(" ", "_")
        ch_start = current_time

        # spacer
        sp = os.path.join(ep_dir, f"ch_{ch_idx:02d}_spacer.wav")
        current_time += get_dur(sp)

        for b in ch.get("beats", []):
            wp = os.path.join(ep_dir, f"{b['beat_id']}_voice.wav")
            current_time += get_dur(wp)

        ch_end = current_time
        ch_out = os.path.join(output_dir, f"{ch_idx:02d}_{ch_name}.mp4")
        print(f"Chapter {ch_idx}: {ch['chapter_title']} ({ch_start:.2f}s - {ch_end:.2f}s, dur: {ch_end - ch_start:.2f}s)")

        subprocess.run([
            "ffmpeg", "-y", "-ss", f"{ch_start:.2f}", "-to", f"{ch_end:.2f}",
            "-i", master_video, "-c", "copy", ch_out
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Created: {ch_out} ({os.path.getsize(ch_out) / 1024 / 1024:.2f} MB)")

    print("All chapters sliced successfully!")

if __name__ == "__main__":
    main()
