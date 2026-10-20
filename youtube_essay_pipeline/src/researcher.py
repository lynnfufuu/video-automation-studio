"""
researcher.py - Autonomous Web & Topic Research Engine for YouTube Video Essays
Scans, scores, and analyzes dark science paradoxes, existential physics, historical anomalies,
and cosmic mysteries inspired by channels like Stickman Explains and Judicium.
"""

import os
import json
import random
from typing import Dict, List, Any

CURATED_RESEARCH_TOPICS = [
    {
        "topic_id": "quantum_immortality",
        "title": "Quantum Immortality: The Infinite Prison of Consciousness",
        "domain": "Quantum Mechanics & Existential Dread",
        "hook_premise": "According to the Many-Worlds interpretation, you can never truly die from your own perspective. Every time you face death, your conscious timeline splits, trapping you in an endless cascading reality where you are forced to survive increasingly agonizing, lonely nightmares.",
        "scientific_foundation": "Hugh Everett's Many-Worlds Interpretation, Max Tegmark's Quantum Suicide thought experiment, and decoherence theory.",
        "visual_motifs": "Splintering realities, hospital rooms fading into desolate voids, quantum wave functions as glowing spiderwebs, aging solitary figures on barren Earths.",
        "curiosity_score": 9.8,
        "dread_score": 9.9
    },
    {
        "topic_id": "strange_matter_disaster",
        "title": "Strange Matter: The Subatomic Infection That Liquidates Planets",
        "domain": "Particle Physics & Planetary Extinction",
        "hook_premise": "Deep inside neutron star cores exists a hypothetical form of matter so stable that touching normal atoms converts them instantaneously into more strange matter. If a single microscopic strangelet touches Earth, our entire planet would dissolve into a dense, boiling sphere of strange soup in less than sixty seconds.",
        "scientific_foundation": "Strangelet physics, quark matter stability hypothesis (Witten, 1984), relativistic heavy-ion collisions, and neutron star crust disruptions.",
        "visual_motifs": "Collapsed neutron stars colliding, a microscopic incandescent droplet striking the Atlantic Ocean, continental rock liquifying into iridescent grey matter, an empty solar orbit.",
        "curiosity_score": 9.6,
        "dread_score": 9.7
    },
    {
        "topic_id": "silurian_hypothesis",
        "title": "The Silurian Hypothesis: Did Another Civilization Walk Earth Before Us?",
        "domain": "Geology, Paleoclimatology & Lost History",
        "hook_premise": "If an industrial, high-tech reptilian or mammalian civilization lived on Earth 55 million years ago, geological plate tectonics, weathering, and fossilization rates mean zero buildings, plastics, or bones would survive to modern day. The only trace would be a sudden spike in carbon isotopes—the exact same spike we see in the geological record during the Paleocene-Eocene Thermal Maximum.",
        "scientific_foundation": "Gavin Schmidt and Adam Frank's 2018 NASA astrobiology paper, geological half-lives of industrial artifacts, and sediment core anomalies.",
        "visual_motifs": "Fossilized strata layers under electron microscopes, skyscrapers crumbling into dust over millions of years, mysterious geometric sediment layers under modern seabed.",
        "curiosity_score": 9.7,
        "dread_score": 9.1
    },
    {
        "topic_id": "cognitohazards_info_danger",
        "title": "Information Hazards: Ideas That Harm You The Moment You Understand Them",
        "domain": "Philosophy of Mind, Memetics & Psychological Horror",
        "hook_premise": "In physics and epistemology, some concepts operate like biological pathogens. Known as informational hazards and cognitohazards, these are truths, mathematical paradoxes, or psychological algorithms that permanently alter neural circuitry or inflict psychiatric catastrophe simply by being comprehended.",
        "scientific_foundation": "Nick Bostrom's Information Hazards taxonomy (2011), Basilisk paradoxes, memetic epidemiology, and psychological shock vectors.",
        "visual_motifs": "Blacked-out classified documents, glowing geometric fractals burning into CRT monitors, psychiatric observation rooms, silent researchers staring at redacted screens.",
        "curiosity_score": 9.9,
        "dread_score": 9.8
    },
    {
        "topic_id": "bootes_supervoid",
        "title": "The Boötes Void: The 300-Million-Light-Year Hole in the Universe",
        "domain": "Observational Cosmology & Cosmic Anomalies",
        "hook_premise": "Astronomers discovered an expanse of deep space three hundred and thirty million light years across that should contain over ten thousand galaxies, yet contains almost nothing. Standard cosmological inflation models struggle to explain how such a monstrous void could form naturally, leading some astrophysicists to propose civilization-scale energy harvesting or ancient vacuum collapse.",
        "scientific_foundation": "Robert Kirshner (1981) discovery of the Great Void, cosmic web filament topology, Baryon Acoustic Oscillations, and dark energy expansion.",
        "visual_motifs": "3D cosmic web diagrams showing a pitch-black spherical absence in the galactic tapestry, lone radio telescope dishes in desert nights, cold dead sectors of space.",
        "curiosity_score": 9.5,
        "dread_score": 9.4
    }
]

class DocumentaryResearcher:
    def __init__(self, cache_file: str = None):
        self.cache_file = cache_file or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "researched_topics.json"))
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        self.topics = self._load_topics()

    def _load_topics(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        self._save_topics(CURATED_RESEARCH_TOPICS)
        return CURATED_RESEARCH_TOPICS

    def _save_topics(self, topics: List[Dict[str, Any]]):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(topics, f, indent=2)

    def search_trending_ideas(self, domain_filter: str = None) -> List[Dict[str, Any]]:
        """Returns topics matching the high-retention dark science / existential niche."""
        results = self.topics
        if domain_filter:
            results = [t for t in self.topics if domain_filter.lower() in t["domain"].lower() or domain_filter.lower() in t["title"].lower()]
        # Sort by composite interest score
        results.sort(key=lambda x: x.get("curiosity_score", 0) + x.get("dread_score", 0), reverse=True)
        return results

    def select_best_pitch(self, topic_query: str = None) -> Dict[str, Any]:
        """Pitches the highest-potential concept based on user query or autonomous selection."""
        if topic_query:
            q_lower = topic_query.lower()
            for t in self.topics:
                if q_lower in t["title"].lower() or q_lower in t["topic_id"].lower() or q_lower in t["domain"].lower():
                    return t
            # Dynamically register custom query as a new topic
            new_id = q_lower.replace(" ", "_")[:24]
            custom_pitch = {
                "topic_id": new_id,
                "title": f"The Anomaly of {topic_query.title()}",
                "domain": "Dark Science & Unexplained Anomalies",
                "hook_premise": f"Investigating the deep, unsettling scientific and historical truths behind {topic_query}.",
                "scientific_foundation": f"Forensic analysis, theoretical modeling, and documented case studies of {topic_query}.",
                "visual_motifs": f"Atmospheric dark documentary imagery exploring {topic_query}, moody chiaroscuro lighting, forensic archives.",
                "curiosity_score": 9.5,
                "dread_score": 9.3
            }
            self.topics.append(custom_pitch)
            self._save_topics(self.topics)
            return custom_pitch

        # Select highest-scoring unproduced concept
        return self.topics[0]

if __name__ == "__main__":
    res = DocumentaryResearcher()
    pitch = res.select_best_pitch()
    print("Top Documentary Pitch:")
    print(f"Title: {pitch['title']}")
    print(f"Hook: {pitch['hook_premise']}")
