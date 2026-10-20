import json
import wave
import os

root = r"C:\Users\yoshikiinyein\.gemini\antigravity\scratch\youtube_essay_pipeline"
ep_dir = os.path.join(root, "assets", "episodes", "japanese_urban_legends")
script_path = os.path.join(root, "data", "japanese_urban_legends.json")

with open(script_path, "r", encoding="utf-8") as f:
    script = json.load(f)

missing_images = []
missing_audio = []

for b in script.get("intro_hook", {}).get("beats", []):
    img = os.path.join(ep_dir, f"{b['beat_id']}_flux.jpg")
    aud = os.path.join(ep_dir, f"{b['beat_id']}_voice.wav")
    if not os.path.exists(img): missing_images.append(img)
    if not os.path.exists(aud): missing_audio.append(aud)

for ch in script["chapters"]:
    ch_idx = ch["chapter_index"]
    tc = os.path.join(ep_dir, f"ch_{ch_idx:02d}_titlecard.jpg")
    sp = os.path.join(ep_dir, f"ch_{ch_idx:02d}_spacer.wav")
    if not os.path.exists(tc): missing_images.append(tc)
    if not os.path.exists(sp): missing_audio.append(sp)
    for b in ch["beats"]:
        img = os.path.join(ep_dir, f"{b['beat_id']}_flux.jpg")
        aud = os.path.join(ep_dir, f"{b['beat_id']}_voice.wav")
        if not os.path.exists(img): missing_images.append(img)
        if not os.path.exists(aud): missing_audio.append(aud)

print(f"Missing images: {len(missing_images)}")
print(f"Missing audio: {len(missing_audio)}")
print(f"Total verified beats + cards: {len(script.get('intro_hook', {}).get('beats', [])) + sum(len(c['beats']) + 1 for c in script['chapters'])}")
