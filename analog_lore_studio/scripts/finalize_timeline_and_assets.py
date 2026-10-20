import json
import os
import shutil
import cv2
import numpy as np

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
scenes_dir = os.path.join(base_dir, "assets", "ai_scenes")
timeline_path = os.path.join(base_dir, "data", "timeline.json")

# Clean up any remaining files that had timestamps
# 1. opt2_sc1_entry_angle1: copy opt2_sc1_entry_angle2 to it (clean 1440x1080 mall concourse)
clean_mall = os.path.join(scenes_dir, "opt2_sc1_entry_angle2.jpg")
if os.path.exists(clean_mall):
    im_mall = cv2.imread(clean_mall)
    # Flip horizontally for angle 1 so angle 1 and angle 2 are distinct views of the mall!
    im_mall_flip = cv2.flip(im_mall, 1)
    cv2.imwrite(os.path.join(scenes_dir, "opt2_sc1_entry_angle1.jpg"), im_mall_flip)
    cv2.imwrite(os.path.join(scenes_dir, "opt2_sc1_entry.jpg"), im_mall)
    print("Created clean opt2_sc1_entry_angle1.jpg and opt2_sc1_entry.jpg")

# 2. opt3_sc6_verdict_angle1: copy clean subterranean corridor to it
clean_tunnel = os.path.join(base_dir, "output", "steam_burst_clean.jpg")
if os.path.exists(clean_tunnel):
    shutil.copy2(clean_tunnel, os.path.join(scenes_dir, "opt3_sc6_verdict_angle1.jpg"))
    shutil.copy2(clean_tunnel, os.path.join(scenes_dir, "opt3_sc6_verdict.jpg"))
    print("Created clean opt3_sc6_verdict_angle1.jpg")

# 3. Update timeline.json so scenes have clean, 2-still or 3-still cinematic setups
with open(timeline_path, "r", encoding="utf-8") as f:
    meta = json.load(f)

for sc in meta["timeline"]:
    sc_id = sc["scene_id"]
    if sc_id == "hook_01_three_doors":
        sc["stills"] = [
            {"still_id": "hook_01_three_doors_angle1", "angle_name": "THREE DOORS SIDE BY SIDE", "focus": "wide"},
            {"still_id": "hook_01_three_doors_angle2", "angle_name": "CRT TV HEAD ENTITY", "focus": "entity"},
            {"still_id": "hook_01_three_doors_angle3", "angle_name": "SUB-LEVEL CORRIDOR PERSPECTIVE", "focus": "corridor"}
        ]
    else:
        # 2 distinct, highly cinematic stills per scene:
        # Still 1: Wide establishing/area shot
        # Still 2: Specific script mention (rations, entity, dripping pipe, vents, etc.)
        sc["stills"] = [
            {"still_id": f"{sc_id}_angle1", "angle_name": "AREA PERSPECTIVE", "focus": "wide"},
            {"still_id": f"{sc_id}_angle2", "angle_name": "SCRIPT DETAIL", "focus": "detail"}
        ]

with open(timeline_path, "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

print("Updated data/timeline.json successfully!")
