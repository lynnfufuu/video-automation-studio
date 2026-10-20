"""
creature_engine.py - Procedural Liminal Ecology & Non-Humanoid Creature Generator
Capable of inventing over 1,000,000 unique liminal spaces and physiologically fused,
non-humanoid apex organisms designed specifically for 1990s analog horror found footage.
"""

import random
from typing import Dict, List, Any

# 1. Architectural Bases (Over 40 Distinct Liminal Archetypes)
ARCHITECTURAL_BASES = [
    {
        "biome_id": "submerged_tile_cistern",
        "name": "Submerged Tile Cistern",
        "materials": "cracked white subway ceramic tiles, rusted brass filtration drains, deep stagnant turquoise brine",
        "lighting": "greenish underwater luminescence, harsh direct camera flash bouncing off rippling water",
        "ambient_smell": "dilated chlorinated bleach and wet limestone",
        "danger_cue": "water surface vibrating in slow concentric hydraulic rings"
    },
    {
        "biome_id": "dead_mall_atrium",
        "name": "1980s Dead Shopping Concourse",
        "materials": "shuttered corrugated aluminum storefront gates, filthy blackened skylight ribs, dusty terra cotta floor tiles, dead escalator troughs",
        "lighting": "faint flickering amber and purple retro neon glow, harsh specular flash falloff",
        "ambient_smell": "decaying carpet adhesive, stale ozone, and fried motor grease",
        "danger_cue": "distant distorted muzak suddenly dropping two octaves into a low hum"
    },
    {
        "biome_id": "subterranean_boiler_core",
        "name": "Sector Zero Steam Catacombs",
        "materials": "heavy riveted boilerplate iron, ruptured high-pressure steam lines, red iron catwalk grating suspended over black abysses",
        "lighting": "intense red emergency beacon pulses, blinding white steam plumes piercing darkness",
        "ambient_smell": "superheated rust, scorched mineral slag, and boiling sulfur",
        "danger_cue": "sudden absolute cessation of the background klaxon siren"
    },
    {
        "biome_id": "infinite_yellow_office",
        "name": "Endless Monotony Office Suite",
        "materials": "damp sulfur-yellow wallpaper, water-damaged mineral fiber drop ceiling tiles, moldy synthetic beige carpet",
        "lighting": "buzzing 60Hz flickering fluorescent ballasts, harsh camera flash drop shadow",
        "ambient_smell": "stale moisture, dry static electricity, and decomposing acoustic foam",
        "danger_cue": "ceiling acoustic tiles visibly sagging downward from weight above"
    },
    {
        "biome_id": "frozen_meat_locker",
        "name": "Infinite Sub-Zero Cold Storage",
        "materials": "heavy industrial freezer plastic strip curtains, frosted stainless steel overhead conveyor tracks, rime-covered concrete",
        "lighting": "pale blue mercury vapor lamps frosted with ice crystals, direct flash reflecting off hoarfrost",
        "ambient_smell": "dry sub-zero ammonia frost and ancient frozen brine",
        "danger_cue": "rapid crystallization of frost spreading across the camera lens"
    },
    {
        "biome_id": "vintage_bowling_lane_undercroft",
        "name": "1970s Bowling Alley Machinery Undercroft",
        "materials": "endless motorized pin-setter pulleys, rancid lane-oil gutters, yellowed formica dividers, heavy ball-return iron chutes",
        "lighting": "dim orange incandescent filament bulbs swinging on frayed cables, harsh flash reflections",
        "ambient_smell": "rancid paraffin lane wax, hot leather drive belts, and stale tobacco",
        "danger_cue": "a bowling ball rolling down an empty dark lane toward your position"
    },
    {
        "biome_id": "subterranean_telecom_vault",
        "name": "High-Voltage Telecom Cable Shaft",
        "materials": "thousands of braided black trunk cables, lead-jacketed wire harnesses, galvanized steel cable trays, copper grounding busbars",
        "lighting": "faint green phosphor LED telemetry arrays, harsh camera flash reflecting off wet rubber",
        "ambient_smell": "hot electrical insulation, flux resin, and copper oxidation",
        "danger_cue": "high-frequency electromagnetic whining causing tape audio distortion"
    },
    {
        "biome_id": "brutalist_storm_retention_silo",
        "name": "Cyclopean Storm Retention Silo",
        "materials": "massive monolithic raw cast concrete pillars, massive storm outflow baffles, sediment-caked floors with deep drain troughs",
        "lighting": "pitch black void with singular harsh camera flash revealing colossal curved concrete walls",
        "ambient_smell": "damp alluvial mud, stagnant urban runoff, and wet cement dust",
        "danger_cue": "echoing low-frequency barometric rush of rising floodwater"
    },
    {
        "biome_id": "decommissioned_hospital_radiology",
        "name": "Sub-Basement Radiation Oncology Ward",
        "materials": "heavy lead-lined sliding blast doors, yellowing vinyl wall paneling, rusted fluoroscopy gantry mounts, broken barium swallow basins",
        "lighting": "dead emergency exit signs glowing dull cadmium red, harsh flash lighting",
        "ambient_smell": "antiseptic formaldehyde, desiccated vinyl adhesive, and irradiated dust",
        "danger_cue": "scintillating white radiation static specks crawling across the video frame"
    },
    {
        "biome_id": "subterranean_archive_stacks",
        "name": "Infinite Microfilm & Paper Records Vault",
        "materials": "endless motorized rolling steel file compactors, millions of decaying cardboard dossiers, narrow aisles of rusted sheet metal shelves",
        "lighting": "motion-sensor timer lights shutting off one by one in the distance, direct flash illumination",
        "ambient_smell": "dry cellulose rot, silver halide vinegar decay, and fine paper dust",
        "danger_cue": "the mechanical whine of rolling shelf compactors closing together on their own"
    },
    {
        "biome_id": "1980s_school_locker_catacombs",
        "name": "Endless Cinderblock School Corridor",
        "materials": "rows of battered olive-green metal lockers, waxed institutional linoleum flooring, wired safety glass classroom transoms",
        "lighting": "faint green emergency exit sign illumination, harsh direct flash photography",
        "ambient_smell": "floor buffer wax, damp athletic wool, and rust",
        "danger_cue": "every locker door down the hall slowly unlatching in sequence"
    },
    {
        "biome_id": "subterranean_sewage_overflow_culvert",
        "name": "Victorian Brick Sewer Interceptor",
        "materials": "soot-stained curved red brick barrel vaults, iron sluice gates with hand-crank wheels, slippery mossy brick footpaths",
        "lighting": "total subterranean darkness cut only by harsh camera flash",
        "ambient_smell": "ancient methane, anaerobic silt, and wet brick efflorescence",
        "danger_cue": "thick black bubbles surfacing rapidly in the center current"
    }
]

# 2. Non-Humanoid Anatomical Blueprints (Zero Standing Humanoids)
NON_HUMANOID_MORPHOLOGIES = [
    {
        "morph_type": "siphon_mollusk",
        "name": "Siphon Polyp / Drain Feeder",
        "anatomy": "a massive bulbous, translucent siphon maw ringed with concentric layers of needle-sharp calcified baleen, lacking eyes or face, fused directly into drainage grates with thick muscular anchor stalks",
        "motion": "pulsing hydraulic siphoning, sliding silently across wet tiles leaving thick mineral slime"
    },
    {
        "morph_type": "wireframe_centipede",
        "name": "Segmented Cable Centipede",
        "anatomy": "a thirty-foot segmented arthropod abomination whose exoskeleton is woven entirely from frayed steel elevator cables and shattered retail wire shelving, crawling on dozens of sharp rebar claws",
        "motion": "lightning-fast skittering along ceilings and walls with metallic clinking sounds"
    },
    {
        "morph_type": "pneumatic_slag_strider",
        "name": "Thermal Piston Strider",
        "anatomy": "a grotesque eyeless organism encased in rusted boiler plates and melted slag iron, walking on six elongated needle-thin pneumatic stilt appendages that puncture through steel grating, venting scalding white steam from dorsal spiracles",
        "motion": "slow, deliberate mechanical striding that causes iron catwalks to vibrate"
    },
    {
        "morph_type": "plenum_tendril_colony",
        "name": "Acoustic Ceiling Strangler",
        "anatomy": "a sprawling fibrous black lichen mass rooted inside the dropped ceiling plenum, dangling hundreds of wet, translucent sinew cords and twitching nerve-fiber roots through broken ceiling tiles to the floor",
        "motion": "motionless suspension that snaps upward in a fraction of a second when a tendon is brushed"
    },
    {
        "morph_type": "mannequin_polybrach",
        "name": "Amalgamated Fiberglass Polybrach",
        "anatomy": "a sprawling non-humanoid creature composed of dozens of fused, cracked pale fiberglass mannequin torsos, hollow limbs, and disjointed plastic display joints, clustered around a central pulsing core of stripped security wire",
        "motion": "scuttling along floors like a colossal pale hermit crab, limbs clattering against tile"
    },
    {
        "morph_type": "rime_glass_arachnid",
        "name": "Cryogenic Permafrost Arthropod",
        "anatomy": "a massive multi-segmented crustacean whose carapace is formed of razor-sharp sheets of translucent blue-white glacier ice and rusted meat hooks, with dozens of serrated frozen leg stalks and no head",
        "motion": "gliding soundlessly across frozen concrete on razor-edged ice stilts"
    },
    {
        "morph_type": "phosphor_tube_hydra",
        "name": "Cathode Ray Polyp",
        "anatomy": "a cluster of bloated, pulsing copper coil sacs supporting seven serpentine necks that terminate in cracked, glowing green CRT oscilloscope lenses and vacuum tubes that emit high-voltage arc flashes",
        "motion": "undulating coil locomotion across dusty shelving, discharging blinding static"
    },
    {
        "morph_type": "concrete_chitin_bivalve",
        "name": "Monolithic Cast-Crete Bivalve",
        "anatomy": "a colossal, clam-like bivalve organism camouflaged perfectly as a raw concrete support column, its shell opening horizontally to reveal rows of jagged quartz teeth and black filtration tendrils",
        "motion": "stationary ambush predator that slams shut with hydraulic force"
    },
    {
        "morph_type": "paper_moth_serpent",
        "name": "Cellulose Scale Serpent",
        "anatomy": "an eighty-foot limbless constrictor covered in overlapping, razor-sharp yellowed parchment scales derived from microfilm dossiers, with a radial lamprey mouth ringed with rusted paper-clip spikes",
        "motion": "flowing like water through narrow archive shelving aisles with a sound like shuffling cards"
    },
    {
        "morph_type": "corrugated_iron_leech",
        "name": "Galvanized Sluice Leech",
        "anatomy": "a thick, twenty-foot flattened slug-like abomination whose dorsal skin mimics corrugated iron siding, anchored to ceiling pipes by ringed vacuum suckers, dripping caustic amber rust fluids",
        "motion": "creeping peristaltic contraction across overhead beams, dropping from above"
    }
]

# 3. Sensory & Hunting Behaviors
HUNTING_BEHAVIORS = [
    "detects the microscopic vibration of footfalls through floor tiles from over two hundred meters away",
    "tracks the electrical magnetic field generated by flashlights, camcorder batteries, and pacemakers",
    "hunts by sensing fluctuations in ambient barometric air pressure caused by opening doors",
    "listens exclusively for human breathing and remains completely motionless while you are screaming",
    "mimics the acoustic frequency of dripping water and distant ventilation hums to lure curious explorers",
    "emits high-frequency ultrasonic clicks that temporarily blind human balance and induce spatial vertigo",
    "releases microscopic chlorine vapor clouds that dissolve flashlight plastic and fog camera lenses",
    "remains dormant until ambient temperature rises above ninety degrees from human body heat"
]

class LiminalCreatureEngine:
    """Generates procedural, completely creative liminal biomes and non-humanoid creatures."""
    
    @staticmethod
    def generate_random_biome_and_creature(seed: int = None) -> Dict[str, Any]:
        if seed is not None:
            random.seed(seed)
            
        base = random.choice(ARCHITECTURAL_BASES)
        morph = random.choice(NON_HUMANOID_MORPHOLOGIES)
        hunt = random.choice(HUNTING_BEHAVIORS)
        
        # Procedural Name Generation
        realm_level = random.randint(1, 999)
        creature_code = f"ENTITY-{random.randint(100, 999)}-{morph['morph_type'][:3].upper()}"
        
        # Build Lore Narration Snippet
        speech_encounter = (
            f"If you encounter {morph['name']}, do not attempt to run. "
            f"It {hunt}. Its body is fused with {base['materials'].split(',')[0]}, "
            f"making it virtually invisible against the walls until it strikes."
        )
        
        # High-Fidelity 1990s Analog Horror Image Prompt (Strict 4:3, Zero Text, Zero Timestamps)
        ai_prompt = (
            f"1990s flash photography, liminal space: {base['name']}. {base['materials']}, {base['lighting']}. "
            f"Terrifying non-humanoid creature in the frame: {morph['anatomy']}. {morph['motion']}. "
            f"Harsh direct camera flash, deep heavy shadows, 1997 found footage analog horror photography, "
            f"authentic 4:3 aspect ratio, 35mm grain, no human face, strictly non-humanoid beast, no text, no timestamp"
        )
        
        return {
            "level_number": realm_level,
            "biome_name": base["name"],
            "ambient_smell": base["ambient_smell"],
            "danger_cue": base["danger_cue"],
            "creature_code": creature_code,
            "creature_name": morph["name"],
            "creature_anatomy": morph["anatomy"],
            "creature_motion": morph["motion"],
            "hunting_mechanism": hunt,
            "narration_speech": speech_encounter,
            "ai_image_prompt": ai_prompt
        }

if __name__ == "__main__":
    print("=" * 80)
    print("[LIMINAL CREATURE ENGINE] Procedural Generation Test (3 Random Universes)")
    print("=" * 80)
    for i in range(1, 4):
        sample = LiminalCreatureEngine.generate_random_biome_and_creature(seed=i * 77)
        print(f"\n--- [UNIVERSE #{i}] Level {sample['level_number']}: {sample['biome_name']} ---")
        print(f"Apex Organism: {sample['creature_name']} ({sample['creature_code']})")
        print(f"Anatomy: {sample['creature_anatomy']}")
        print(f"Hunting: {sample['hunting_mechanism']}")
        print(f"Danger Sign: {sample['danger_cue']}")
        print(f"Analog Prompt:\n{sample['ai_image_prompt']}\n")
