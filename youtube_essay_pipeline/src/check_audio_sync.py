import json
import os
import subprocess

def get_dur(p):
    return float(subprocess.check_output([
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        p
    ]).decode().strip())

root = r"C:\Users\yoshikiinyein\.gemini\antigravity\scratch\youtube_essay_pipeline"
ep_dir = os.path.join(root, "assets", "episodes", "japanese_urban_legends")
concat_file = os.path.join(ep_dir, "speech_concat_list.txt")

with open(concat_file, "r", encoding="utf-8") as f:
    paths = []
    for line in f:
        line = line.strip()
        if line.startswith("file '") and line.endswith("'"):
            paths.append(line[6:-1])

print(f"Total files in concat list: {len(paths)}")
total_dur = 0.0
for i, p in enumerate(paths):
    d = get_dur(p)
    total_dur += d

master_speech = os.path.join(ep_dir, "master_speech.wav")
master_soundtrack = os.path.join(ep_dir, "master_soundtrack.wav")
output_mp4 = os.path.join(root, "output", "youtube_essay_japanese_urban_legends.mp4")

print(f"Sum of audio clips: {total_dur:.4f}s ({total_dur/60:.2f} mins)")
if os.path.exists(master_speech):
    print(f"master_speech.wav: {get_dur(master_speech):.4f}s")
if os.path.exists(master_soundtrack):
    print(f"master_soundtrack.wav: {get_dur(master_soundtrack):.4f}s")
if os.path.exists(output_mp4):
    print(f"current mp4: {get_dur(output_mp4):.4f}s")
