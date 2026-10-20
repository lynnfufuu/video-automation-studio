import shutil
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_dir = os.path.join(base_dir, "output")
scenes_dir = os.path.join(base_dir, "assets", "ai_scenes")

copies = [
    ("test_doors_photorealistic_clean.jpg", "hook_01_three_doors.jpg"),
    ("test_doors_photorealistic_clean.jpg", "hook_01_three_doors_angle1.jpg"),
    ("test_tvhead_doors3.jpg", "hook_01_three_doors_angle2.jpg"),
    ("doors_side_by_side_clean.jpg", "hook_01_three_doors_angle3.jpg"),
    ("clean_opt1_sc1_flawless.jpg", "opt1_sc1_entry_angle1.jpg"),
    ("test_dripping_pipe.jpg", "opt1_sc3_rations_angle2.jpg"),
    ("clean_opt1_sc4.jpg", "opt1_sc4_entities_angle2.jpg"),
    ("mannequin_clean.jpg", "opt2_sc4_entities_angle2.jpg"),
    ("ration_crate_clean.jpg", "opt3_sc3_rations_angle2.jpg"),
    ("steam_burst_clean.jpg", "opt3_sc2_environment_angle2.jpg"),
]

for src_name, dst_name in copies:
    src = os.path.join(output_dir, src_name)
    dst = os.path.join(scenes_dir, dst_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied: {src_name} -> {dst_name}")
    else:
        print(f"Missing: {src_name}")
