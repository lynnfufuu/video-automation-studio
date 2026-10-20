"""
scenario_generator.py - Intelligent Topic & Scenario Director for YouTube & TikTok Studios
Handles:
1. TikTok Scenario Generation:
   - User-described custom prompt (e.g. 'choose 4 planets where each planet has an entity')
   - Autonomous theme rotation (3 doors, 4 planets, 3 elevators, 3 highway exits)
2. YouTube Video Essay Topic Resolution:
   - Single-word genre keywords ('horror', 'myth', 'science', 'space', 'superhero')
   - Full custom documentary queries
   - Outlines title, hook synopsis, and 5-chapter structure
"""

import os
import json
import random
from typing import Dict, Any, Tuple, List

# Pre-defined curated TikTok analog horror themes
TIKTOK_THEMES = [
    {
        "id": "doors",
        "title": "CHOOSE ONE TO SURVIVE: 3 SUB-LEVEL ENTRANCES",
        "hook_speech": "Three sealed blast doors have materialized in the lower maintenance sub-level. One contains survivable terrain. The others lead to terminal non-spaces. Choose your door before the lockdown seals permanently.",
        "options": [
            {"name": "OPTION 1: THE POOLROOMS (LEVEL 37)", "classification": "DECEPTIVE SAFE ZONE", "survival_rate": "78%"},
            {"name": "OPTION 2: THE 1986 DEAD MALL", "classification": "HIGH-RISK PUZZLER", "survival_rate": "31%"},
            {"name": "OPTION 3: SECTOR 0 (RED UTILITY TUNNELS)", "classification": "CLASS: DEADZONE", "survival_rate": "0.01%"}
        ]
    },
    {
        "id": "planets",
        "title": "CHOOSE ONE OF FOUR DERELICT EXOPLANETS",
        "hook_speech": "Your deep-reconnaissance starship has suffered primary atmospheric failure. Four uncharted exoplanets are within orbital insertion range. Each harbors an ancient biological threat. Choose your destination before oxygen depletion.",
        "options": [
            {"name": "PLANET 1: KEPLER-10C (THE GLASS DUNES)", "classification": "EXTREME HEAT / SILICA WINDS", "survival_rate": "64%"},
            {"name": "PLANET 2: GLIESE 1214B (THE TRENCH OCEAN)", "classification": "LEVIATHAN DEPTH HAZARD", "survival_rate": "22%"},
            {"name": "PLANET 3: PROXIMA D (THE SILICON HIVE)", "classification": "ACTIVE PARASITIC SPORES", "survival_rate": "8%"},
            {"name": "PLANET 4: TOI-700E (THE CRYO-ABYSS)", "classification": "SUB-ZERO PREDATOR TERRITORY", "survival_rate": "0.1%"}
        ]
    },
    {
        "id": "elevators",
        "title": "CHOOSE ONE OF THREE ANOMALOUS ELEVATORS",
        "hook_speech": "The subterranean research complex has entered total containment lockdown. Three emergency industrial elevators are operational, each descending into an unmapped floor. Select your elevator before the stairwells flood.",
        "options": [
            {"name": "ELEVATOR A: THE FLOODED SUB-ATRIUM", "classification": "RISING WATER HAZARD", "survival_rate": "71%"},
            {"name": "ELEVATOR B: FLOOR NEGATIVE FORTY", "classification": "AUDITORY COGNITOHAZARD", "survival_rate": "29%"},
            {"name": "ELEVATOR C: THE RUST CARGO SHAFT", "classification": "BIOMECHANICAL INFESTATION", "survival_rate": "0.05%"}
        ]
    },
    {
        "id": "highways",
        "title": "CHOOSE ONE OF THREE MIDNIGHT HIGHWAY EXITS",
        "hook_speech": "You have been driving along Route 9 for four hours without passing a single vehicle. Ahead, three highway exits appear through the static fog. Each exit leads to a separate isolated landmark. Choose where you pull over before your headlights die.",
        "options": [
            {"name": "EXIT 404: THE ABANDONED REST STOP", "classification": "FLICKERING LIGHT SANCTUARY", "survival_rate": "68%"},
            {"name": "EXIT 0: THE PINE FOREST TUNNEL", "classification": "TEMPORAL DISORIENTATION", "survival_rate": "19%"},
            {"name": "EXIT 99: THE DESERT RADIO TOWER", "classification": "BROADCAST TRANSMISSION ENTITY", "survival_rate": "0.02%"}
        ]
    }
]

def generate_tiktok_scenario(prompt: str = None) -> Tuple[str, str, List[Dict[str, str]], Dict[str, Any]]:
    """
    Builds a TikTok scenario from a custom prompt or auto-rotates themes.
    Returns: (title, hook_speech, options_list, full_queue_dict)
    """
    if prompt and prompt.lower() != "auto":
        # Custom user prompt
        clean_prompt = prompt.strip()
        title = f"CHOOSE TO SURVIVE: {clean_prompt.upper()}"
        hook = f"You are faced with a fatal dilemma: {clean_prompt}. One path offers survival. The others lead to terminal anomalies. Choose carefully before time runs out."
        
        # Parse or generate 3-4 options based on keywords
        if "planet" in clean_prompt.lower():
            options = [
                {"name": "PLANET A: THE DUST WASTES", "classification": "ATMOSPHERIC TOXIN", "survival_rate": "62%"},
                {"name": "PLANET B: THE METHANE OCEAN", "classification": "ABYSSAL ENTITY", "survival_rate": "34%"},
                {"name": "PLANET C: THE CRYSTAL CAVERNS", "classification": "BIO-RESONANCE HAZARD", "survival_rate": "11%"},
                {"name": "PLANET D: THE VOID CRATER", "classification": "TERMINAL GRAVITATIONAL ANOMALY", "survival_rate": "0.01%"}
            ]
        elif "elevator" in clean_prompt.lower() or "room" in clean_prompt.lower() or "door" in clean_prompt.lower():
            options = [
                {"name": "CHAMBER 1: THE TILE RESERVOIR", "classification": "FLOODING ANOMALY", "survival_rate": "74%"},
                {"name": "CHAMBER 2: THE ARCHIVE MEZZANINE", "classification": "SHADOW RELOCATION HAZARD", "survival_rate": "28%"},
                {"name": "CHAMBER 3: SUB-LEVEL REDUCTION", "classification": "CRUSHING PRESSURE", "survival_rate": "0.05%"}
            ]
        else:
            options = [
                {"name": f"OPTION 1: THE FIRST CORRIDOR", "classification": "ISOLATION HAZARD", "survival_rate": "65%"},
                {"name": f"OPTION 2: THE DEEP SHELTER", "classification": "HALLUCINATORY FOG", "survival_rate": "30%"},
                {"name": f"OPTION 3: THE UNCHARTED THRESHOLD", "classification": "UNKNOWN ANOMALOUS VECTOR", "survival_rate": "0.1%"}
            ]
    else:
        # Autonomous selection
        theme = random.choice(TIKTOK_THEMES)
        title = theme["title"]
        hook = theme["hook_speech"]
        options = theme["options"]

    # Build queue structure
    queue_dict = {
        "title": title,
        "hook": {"speech": hook},
        "options": options
    }
    return title, hook, options, queue_dict

# Curated YouTube genres and topics
YOUTUBE_GENRES = {
    "horror": {
        "slug": "japanese_urban_legends",
        "title": "Top 5 Scariest Japanese Urban Legends Explained",
        "hook": "What if the worst thing you could imagine wasn't just lurking in the shadows, but waiting for you to look its way? Today, we are examining the top five scariest, most unsettling urban legends from Japan...",
        "chapters": [
            "Hachishakusama: The Eight-Foot Shadow",
            "Teke Teke: Phantom of the Railway Crossing",
            "Kuchisake-onna: The Slit-Mouthed Woman",
            "Aka Manto: The Red Cape in the Fourth Stall",
            "The Inunaki Village Tunnel: The Lawless Anomaly"
        ]
    },
    "science": {
        "slug": "false_vacuum_decay",
        "title": "Top 5 Existential Physics Paradoxes That Could Destroy Reality",
        "hook": "What if the fundamental laws of nature are not solid ground, but a fragile sheet of glass suspended over an infinite abyss? Today, we investigate the five most terrifying paradoxes in modern physics...",
        "chapters": [
            "False Vacuum Decay: The Bubble of True Nothingness",
            "Quantum Immortality: The Infinite Prison of Consciousness",
            "Strange Matter: The Subatomic Infection Liquefying Planets",
            "Boltzmann Brains: The Fluctuation That Invented Your Memories",
            "The Heat Death: Entropy's Final Silence"
        ]
    },
    "myth": {
        "slug": "dark_mythological_entities",
        "title": "Top 5 Darkest Ancient Mythological Entities Erased From History",
        "hook": "Across antiquity, certain gods and cosmic horrors were so feared that speaking their true names was considered a death sentence. Today, we unearth the five darkest primordial entities from ancient folklore...",
        "chapters": [
            "Apep: The Primordial Chaos Serpent That Eats the Sun",
            "The Wendigo: The Cannibalistic Winter Spirit of the North",
            "Tiamat: The Primordial Salt Sea Dragon of Mesopotamia",
            "The Hekatonkheires: The Hundred-Handed Beings of Tartarus",
            "Fenrir: The Wolf Bound to Shatter the Cosmos"
        ]
    },
    "space": {
        "slug": "dark_cosmic_anomalies",
        "title": "Top 5 Darkest Cosmic Anomalies Lurking in Deep Space",
        "hook": "The deeper we point our orbital telescopes into the cosmos, the more clear it becomes: the universe is not just quiet—it is hiding. Today, we investigate five cosmic anomalies that astrophysicists cannot explain...",
        "chapters": [
            "The Boötes Supervoid: The 330-Million-Light-Year Hole in the Universe",
            "The Great Attractor: The Gravitational Monolith Pulling Galaxies",
            "The Dark Forest: Why Alien Civilizations Are Silent in the Dark",
            "Rogue Black Holes: Wandering Invisible Giants of the Milky Way",
            "The CMB Cold Spot: Collision With a Parallel Universe"
        ]
    },
    "superhero": {
        "slug": "dark_superhero_paradoxes",
        "title": "Top 5 Superhero Secrets That Turned Guardians Into Monsters",
        "hook": "We celebrate godlike vigilantes who patrol our skies. But what happens when omnipotent power meets moral rot? Today, we analyze the five darkest superhero paradoxes where protectors became humanity's greatest nightmare...",
        "chapters": [
            "The Corrupted Ideal: When Guardians Decide Peace Requires Terror",
            "The Surveillance Panopticon: Watching Every Citizen in the Name of Safety",
            "Collateral Blood: The Casualties Forgotten by History",
            "The Fabricated Threat: Staging Disasters to Remain In Power",
            "The Final Verdict: When Godlike Beings Decide Humanity Must Fall"
        ]
    }
}

def resolve_youtube_topic(query: str = None) -> Tuple[str, str, str, List[str]]:
    """
    Resolves a single keyword or custom topic query into documentary title, hook, and chapters.
    Returns: (slug, title, hook_synopsis, chapter_titles_list)
    """
    if not query:
        genre_key = "horror"
    else:
        q_lower = query.lower().strip()
        if "horror" in q_lower or "scary" in q_lower or "japan" in q_lower:
            genre_key = "horror"
        elif "science" in q_lower or "physics" in q_lower or "quantum" in q_lower or "decay" in q_lower:
            genre_key = "science"
        elif "myth" in q_lower or "folklore" in q_lower or "legend" in q_lower or "ancient" in q_lower:
            genre_key = "myth"
        elif "space" in q_lower or "cosmic" in q_lower or "void" in q_lower or "galaxy" in q_lower:
            genre_key = "space"
        elif "superhero" in q_lower or "hero" in q_lower or "comic" in q_lower:
            genre_key = "superhero"
        else:
            # Custom query
            clean_title = query.strip()
            if not clean_title.lower().startswith("top") and not clean_title.lower().startswith("the"):
                clean_title = f"Top 5 Unexplained Mysteries of {clean_title.title()}"
            slug = clean_title.lower().replace(" ", "_").replace(":", "")[:32]
            hook = f"An investigative cosmic horror documentary exploring the darkest mysteries, psychological implications, and hidden anomalies of {query}."
            chapters = [
                f"The Discovery: How {query.title()} Defied Scientific Logic",
                f"The First Encounters: Historical Accounts and Evidence",
                f"The Escalation: When the Anomaly Began Spreading",
                f"The Scientific Paradox: Why Modern Theory Fails to Explain It",
                f"The Final Warning: What This Means for Human Survival"
            ]
            return slug, clean_title, hook, chapters

    data = YOUTUBE_GENRES[genre_key]
    return data["slug"], data["title"], data["hook"], data["chapters"]
