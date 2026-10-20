"""
lore_writer.py - Master Production Multi-Still Lore & Prompt Generator (v8.0)
High-Frequency Multi-Still Architecture:
- 3 distinct photographic angles per scene (Wide, Corridor/Corner, Escalating Close-up)
- Full 4:3 edge-to-edge cinematic composition
- Specialized Entity and Ration visual prompts
"""

import os
import json
from typing import Dict, Any

QUEUE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "queue.json"))

MEGALOPHOBIA_4_3_SUFFIX = (
    ", surreal Kane Pixels analog horror photography, impossible non-Euclidean megalophobia architecture, "
    "massive overwhelming scale, shot on 1997 vintage camcorder in pitch darkness with harsh direct flash, "
    "eerie volumetric fog and dust particles floating in the air, unsettling liminal dread, "
    "hyper-detailed Unreal Engine 5.4 path-traced render, dramatic deep shadows, 4:3 aspect ratio"
)

ENTITY_MODIFIER = ", terrifying anomalous entity standing in dark hallway, uncanny horror, glowing eyes, surreal Kane Pixels style, direct harsh flash, 4:3 aspect ratio"
RATION_MODIFIER = ", ominous survival rations on wooden shelf inside dark abandoned bunker, eerie lighting, cinematic horror photography, 4:3 aspect ratio"

THEMES = [
    {
        "theme": "doors",
        "title": "CHOOSE ONE TO SURVIVE: SUB-LEVEL ENTRANCES",
        "hook_speech": "Three sealed blast doors have materialized in the lower maintenance sub-level. One contains survivable terrain. The others lead to terminal non-spaces. Choose your door before the lockdown seals permanently.",
        "hook_prompt": "Three numbered heavy steel blast doors marked 1 2 and 3 lined up side-by-side in a colossal brutalist concrete corridor, flickering overhead emergency fluorescent lights, water reflections on ground" + MEGALOPHOBIA_4_3_SUFFIX,
        "option_1": {
            "name": "OPTION 1: THE POOLROOMS (LEVEL 37)",
            "classification": "DECEPTIVE SAFE ZONE",
            "survival_rate": "78%",
            "scenes": [
                {
                    "scene_id": "opt1_sc1_entry",
                    "scene_type": "environment",
                    "speech": "If you choose Door Number One, you step into Level Thirty-Seven, commonly known as The Poolrooms. The heavy iron door slams shut and the latch dissolves into solid ceramic.",
                    "prompt": "Colossal liminal poolrooms, endless clean white ceramic tiles, warm shallow aquamarine chlorine water reflecting recessed lights, vaulted arches" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt1_sc1_entry_angle1", "angle_name": "WIDE ESTABLISHING", "focus": "wide"},
                        {"still_id": "opt1_sc1_entry_angle2", "angle_name": "CORRIDOR PERSPECTIVE", "focus": "corridor"},
                        {"still_id": "opt1_sc1_entry_angle3", "angle_name": "DISSOLVING LATCH DETAIL", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt1_sc2_environment",
                    "scene_type": "environment",
                    "speech": "The air is humid and smells faintly of chlorinated bleach. Acoustic echoes here are dilated. Footsteps echo for up to twenty seconds, masking the sound of approaching entities.",
                    "prompt": "Vast empty tiled hall filled with knee-deep clear turquoise water, brutalist arches receding into hazy vanishing point, vapor mist rising" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt1_sc2_environment_angle1", "angle_name": "WIDE ARCHES", "focus": "wide"},
                        {"still_id": "opt1_sc2_environment_angle2", "angle_name": "CORNER RECEDING MIST", "focus": "corner"},
                        {"still_id": "opt1_sc2_environment_angle3", "angle_name": "WATER RIPPLE CLOSE-UP", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt1_sc3_rations",
                    "scene_type": "rations",
                    "speech": "For hydration, do not drink the standing pool water, as it causes severe cellular dehydration. Instead, collect the fresh condensation dripping from overhead copper pipes.",
                    "prompt": "Overhead copper pipes dripping clear water into vintage survival canteens inside dark tile corridor" + RATION_MODIFIER,
                    "stills": [
                        {"still_id": "opt1_sc3_rations_angle1", "angle_name": "OVERHEAD PIPE SYSTEM", "focus": "wide"},
                        {"still_id": "opt1_sc3_rations_angle2", "angle_name": "DRIPPING CONDENSATION DROPLETS", "focus": "detail"},
                        {"still_id": "opt1_sc3_rations_angle3", "angle_name": "CANTEEN ON TILED LEDGE", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt1_sc4_entities",
                    "scene_type": "entity",
                    "speech": "Avoid the darker deep-end tunnels. Submerged drain currents harbor shadow ripple anomalies that pull survivors beneath the tiled floors without leaving a wake.",
                    "prompt": "Submerged dark tunnel opening under glowing pool water, ominous black silhouette creature emerging from water" + ENTITY_MODIFIER,
                    "stills": [
                        {"still_id": "opt1_sc4_entities_angle1", "angle_name": "DISTANT WATER SILHOUETTE", "focus": "wide"},
                        {"still_id": "opt1_sc4_entities_angle2", "angle_name": "APPROACHING SHADOW RIPPLE", "focus": "entity"},
                        {"still_id": "opt1_sc4_entities_angle3", "angle_name": "UNSETTLING ENTITY CLOSE-UP", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt1_sc5_protocol",
                    "scene_type": "environment",
                    "speech": "Stay on the elevated dry walkways. Walk toward the hum of the filtration pumps until you reach the maintenance stairwell. Your twenty-four hour survival probability is seventy-eight percent.",
                    "prompt": "Narrow elevated dry tiled walkway winding through infinite calm pool chambers, distant emergency green exit sign reflection" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt1_sc5_protocol_angle1", "angle_name": "ELEVATED WALKWAYS", "focus": "wide"},
                        {"still_id": "opt1_sc5_protocol_angle2", "angle_name": "PUMP MACHINERY SHADOW", "focus": "corridor"},
                        {"still_id": "opt1_sc5_protocol_angle3", "angle_name": "EMERGENCY STAIRWELL EXIT", "focus": "close_up"}
                    ]
                }
            ]
        },
        "option_2": {
            "name": "OPTION 2: THE 1986 DEAD MALL",
            "classification": "HIGH-RISK PUZZLER",
            "survival_rate": "31%",
            "scenes": [
                {
                    "scene_id": "opt2_sc1_entry",
                    "scene_type": "environment",
                    "speech": "If you open Door Number Two, you enter an abandoned multi-tier shopping atrium frozen in nineteen eighty-six. The air smells of old carpet and ozone.",
                    "prompt": "Abandoned 1980s shopping mall atrium at night, dead escalators leading into dark mezzanine, dried potted ficus trees, dim warm skylight" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt2_sc1_entry_angle1", "angle_name": "WIDE ATRIUM ESCALATORS", "focus": "wide"},
                        {"still_id": "opt2_sc1_entry_angle2", "angle_name": "DARK MEZZANINE CORRIDOR", "focus": "corridor"},
                        {"still_id": "opt2_sc1_entry_angle3", "angle_name": "DIRTY ATRIUM SKYLIGH", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt2_sc2_environment",
                    "scene_type": "environment",
                    "speech": "An endless distorted elevator muzak plays from crackling PA speakers. Prolonged exposure causes rapid short-term memory loss within forty minutes.",
                    "prompt": "Corroded public address speaker mounted on a stained mall pillar, empty storefronts in the background with rusted pull-down security grates" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt2_sc2_environment_angle1", "angle_name": "STOREFRONTS & PA SPEAKER", "focus": "wide"},
                        {"still_id": "opt2_sc2_environment_angle2", "angle_name": "RUSTED SECURITY GRATES", "focus": "corridor"},
                        {"still_id": "opt2_sc2_environment_angle3", "angle_name": "CRACKED SPEAKER CONE", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt2_sc3_rations",
                    "scene_type": "rations",
                    "speech": "For sustenance, search the food court stockrooms for intact hermetically sealed steel canned goods. Never touch open beverage dispensers or warm sodas.",
                    "prompt": "Dusty derelict food court kitchen storage room with metal shelves and canned food supplies" + RATION_MODIFIER,
                    "stills": [
                        {"still_id": "opt2_sc3_rations_angle1", "angle_name": "FOOD COURT STOCKROOM", "focus": "wide"},
                        {"still_id": "opt2_sc3_rations_angle2", "angle_name": "SEALED CANNED GOODS SHELF", "focus": "rations"},
                        {"still_id": "opt2_sc3_rations_angle3", "angle_name": "FLASHLIGHT ON RATION LABELS", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt2_sc4_entities",
                    "scene_type": "entity",
                    "speech": "Beware the store mannequins. They only relocate when unobserved. If you turn a corner and notice a mannequin facing toward you, immediately retrace your footsteps.",
                    "prompt": "Eerie faceless vintage retail store mannequins standing in dark corridor of an abandoned department store" + ENTITY_MODIFIER,
                    "stills": [
                        {"still_id": "opt2_sc4_entities_angle1", "angle_name": "DISTANT MANNEQUINS GROUP", "focus": "wide"},
                        {"still_id": "opt2_sc4_entities_angle2", "angle_name": "MANNEQUIN FACING CAMERA", "focus": "entity"},
                        {"still_id": "opt2_sc4_entities_angle3", "angle_name": "FACELESS UNSETTLING GAZE", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt2_sc5_protocol",
                    "scene_type": "environment",
                    "speech": "Cover your ears with cloth to mitigate the audio hazard, stay away from reflective store glass, and reach the loading bay before midnight. Survival rate is thirty-one percent.",
                    "prompt": "Dark industrial mall loading dock with heavy rubber strip curtains and cold steel exit doors, single amber emergency beacon glowing" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt2_sc5_protocol_angle1", "angle_name": "WIDE LOADING BAY", "focus": "wide"},
                        {"still_id": "opt2_sc5_protocol_angle2", "angle_name": "RUBBER STRIP CURTAINS", "focus": "corridor"},
                        {"still_id": "opt2_sc5_protocol_angle3", "angle_name": "AMBER BEACON LIGHT", "focus": "close_up"}
                    ]
                }
            ]
        },
        "option_3": {
            "name": "OPTION 3: SECTOR 0 (RED UTILITY TUNNELS)",
            "classification": "CLASS: DEADZONE",
            "survival_rate": "0.01%",
            "scenes": [
                {
                    "scene_id": "opt3_sc1_entry",
                    "scene_type": "environment",
                    "speech": "Door Number Three leads straight down into Sector Zero. The heavy airlock seals automatically, locking you into a subterranean network bathed in crimson emergency strobes.",
                    "prompt": "Subterranean industrial utility tunnel bathed in deep ominous crimson red emergency lighting, rusty steam pipes running along curved ceiling" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt3_sc1_entry_angle1", "angle_name": "WIDE CRIMSON AIRLOCK", "focus": "wide"},
                        {"still_id": "opt3_sc1_entry_angle2", "angle_name": "CURVED TUNNEL PERSPECTIVE", "focus": "corridor"},
                        {"still_id": "opt3_sc1_entry_angle3", "angle_name": "RED EMERGENCY STROBE", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt3_sc2_environment",
                    "scene_type": "environment",
                    "speech": "The ambient temperature exceeds one hundred and ten degrees. High pressure steam pipes periodically rupture without warning, causing instantaneous third-degree burns.",
                    "prompt": "Industrial catwalk enveloped in thick boiling white steam plumes, glowing red pipe valves, peeling industrial lead paint" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt3_sc2_environment_angle1", "angle_name": "STEAM CATWALK", "focus": "wide"},
                        {"still_id": "opt3_sc2_environment_angle2", "angle_name": "RUPTURED VALVE STEAM JET", "focus": "corridor"},
                        {"still_id": "opt3_sc2_environment_angle3", "angle_name": "BOILING PRESSURE GAUGE", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt3_sc3_rations",
                    "scene_type": "rations",
                    "speech": "You will spot green emergency ration crates placed conveniently in junctions. Do not touch them. These are mimic bait deployed by indigenous predators to trap starving survivors.",
                    "prompt": "Weathered olive drab military supply crate sitting isolated in a dark crimson tunnel" + RATION_MODIFIER,
                    "stills": [
                        {"still_id": "opt3_sc3_rations_angle1", "angle_name": "JUNCTION CRATE WIDE", "focus": "wide"},
                        {"still_id": "opt3_sc3_rations_angle2", "angle_name": "OLIVE DRAB CRATE STENCIL", "focus": "rations"},
                        {"still_id": "opt3_sc3_rations_angle3", "angle_name": "MIMIC CLAW MARKS ON LATCH", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt3_sc4_entities",
                    "scene_type": "entity",
                    "speech": "The primary entity in Sector Zero mimics the desperate voices of your relatives calling for help. It navigates entirely by flashlight beams and acoustic resonance.",
                    "prompt": "Terrifying tall shadowy gaunt figure lurking at the far end of a red steam tunnel" + ENTITY_MODIFIER,
                    "stills": [
                        {"still_id": "opt3_sc4_entities_angle1", "angle_name": "DISTANT GAUNT SILHOUETTE", "focus": "wide"},
                        {"still_id": "opt3_sc4_entities_angle2", "angle_name": "APPROACHING TALL CREATURE", "focus": "entity"},
                        {"still_id": "opt3_sc4_entities_angle3", "angle_name": "PALE EYES IN RED SHADOW", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt3_sc5_protocol",
                    "scene_type": "environment",
                    "speech": "The moment the background klaxon siren ceases, you must immediately extinguish all light sources and drop flat against the grating. Any movement is fatal.",
                    "prompt": "First person POV looking down a pitch black metal corridor with dying red emergency strobe, flash of sparks from ceiling conduit" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt3_sc5_protocol_angle1", "angle_name": "GRATING FLOOR POV", "focus": "wide"},
                        {"still_id": "opt3_sc5_protocol_angle2", "angle_name": "SPARKS FROM CONDUIT", "focus": "corridor"},
                        {"still_id": "opt3_sc5_protocol_angle3", "angle_name": "PITCH BLACK ABYSS AHEAD", "focus": "close_up"}
                    ]
                },
                {
                    "scene_id": "opt3_sc6_verdict",
                    "scene_type": "environment",
                    "speech": "No documented explorer has ever reached the surface from Sector Zero. Your calculated twenty-four hour survival rate is zero point zero one percent. Which door did you choose?",
                    "prompt": "Sub-level blast door sealed with massive hydraulic locking bolts, painted with decayed yellow radiation hazard stripes" + MEGALOPHOBIA_4_3_SUFFIX,
                    "stills": [
                        {"still_id": "opt3_sc6_verdict_angle1", "angle_name": "SEALED HYDRAULIC DOOR", "focus": "wide"},
                        {"still_id": "opt3_sc6_verdict_angle2", "angle_name": "HAZARD RADIATION STRIPES", "focus": "corridor"},
                        {"still_id": "opt3_sc6_verdict_angle3", "angle_name": "PERMANENT LOCKDOWN SEAL", "focus": "close_up"}
                    ]
                }
            ]
        }
    }
]

def generate_infinite_episode(video_id: str = "liminal_doors_ep01") -> Dict[str, Any]:
    """Generates an episode matching the v8.0 multi-still 4:3 analog horror specification."""
    theme_data = THEMES[0]
    
    episode = {
        "video_id": video_id,
        "theme": theme_data["theme"],
        "title": theme_data["title"],
        "hook": {
            "scene_id": "hook_01_three_doors",
            "scene_type": "environment",
            "speech": theme_data["hook_speech"],
            "prompt": theme_data["hook_prompt"],
            "stills": [
                {"still_id": "hook_01_three_doors_angle1", "angle_name": "THREE DOORS WIDE", "focus": "wide"},
                {"still_id": "hook_01_three_doors_angle2", "angle_name": "DOORS 1 AND 2 LOCKS", "focus": "corridor"},
                {"still_id": "hook_01_three_doors_angle3", "angle_name": "NUMBER STENCIL CLOSE-UP", "focus": "close_up"}
            ]
        },
        "options": [
            {
                "option_index": 1,
                "name": theme_data["option_1"]["name"],
                "classification": theme_data["option_1"]["classification"],
                "survival_rate": theme_data["option_1"]["survival_rate"],
                "scenes": theme_data["option_1"]["scenes"]
            },
            {
                "option_index": 2,
                "name": theme_data["option_2"]["name"],
                "classification": theme_data["option_2"]["classification"],
                "survival_rate": theme_data["option_2"]["survival_rate"],
                "scenes": theme_data["option_2"]["scenes"]
            },
            {
                "option_index": 3,
                "name": theme_data["option_3"]["name"],
                "classification": theme_data["option_3"]["classification"],
                "survival_rate": theme_data["option_3"]["survival_rate"],
                "scenes": theme_data["option_3"]["scenes"]
            }
        ]
    }
    
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump({"queue": [episode]}, f, indent=2)
        
    print(f"[LORE v8.0] Master episode generated with high-frequency multi-stills: {episode['title']}")
    return episode

if __name__ == "__main__":
    generate_infinite_episode()
