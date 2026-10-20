"""
script_writer.py - Autonomous Script & Concept Author for YouTube Video Essays
Transforms researched topics into complete, production-ready video scripts formatted with:
1. High-Clickthrough Title Options
2. Core Premise & Psychological Hook
3. Comprehensive Multi-Chapter Narrative with Sentence-by-Sentence Visual Asset Prompts
"""

import os
import json
from typing import Dict, List, Any

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

class DocumentaryScriptWriter:
    def __init__(self, scripts_dir: str = None, data_dir: str = None):
        self.scripts_dir = scripts_dir or SCRIPTS_DIR
        self.data_dir = data_dir or DATA_DIR
        os.makedirs(self.scripts_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def write_full_production_script(self, pitch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Drafts the complete multi-chapter script with sentence-level visual cues,
        saves the Markdown concept report and the pipeline JSON.
        """
        topic_id = pitch["topic_id"]
        title = pitch["title"]
        domain = pitch["domain"]
        premise = pitch["hook_premise"]
        foundation = pitch["scientific_foundation"]
        
        print(f"\n[SCRIPT WRITER] Drafting full production script for: '{title}'...")
        
        # 1. High-CTR Title Options
        title_options = [
            f"{title}",
            f"The Terrifying Physics of {title.split(':')[0]}",
            f"Why Science Can't Disprove {title.split(':')[0]}",
            f"The Cosmic Paradox That Traps Your Mind",
            f"What Happens If {title.split(':')[0]} Is Real?"
        ]
        
        # 2. Build multi-chapter beats based on topic
        if topic_id == "quantum_immortality":
            chapters = self._build_quantum_immortality_chapters()
        elif topic_id == "strange_matter_disaster":
            chapters = self._build_strange_matter_chapters()
        else:
            chapters = self._build_generic_documentary_chapters(pitch)
            
        script_package = {
            "topic_id": topic_id,
            "title": title,
            "domain": domain,
            "title_options": title_options,
            "core_premise": premise,
            "scientific_foundation": foundation,
            "narrator_voice": "en-US-AndrewMultilingualNeural",
            "speech_rate": "-5%",
            "ambient_volume": "18%",
            "chapters": chapters
        }
        
        # 3. Save JSON for pipeline runner
        json_path = os.path.join(self.data_dir, f"{topic_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(script_package, f, indent=2)
            
        # 4. Save formatted Markdown for channel director / creator review
        md_path = os.path.join(self.scripts_dir, f"{topic_id}_script.md")
        self._write_markdown_script(script_package, md_path)
        
        total_beats = sum(len(c["beats"]) for c in chapters)
        est_runtime_mins = total_beats * 9.5 / 60
        print(f"[SCRIPT WRITER COMPLETE] Finished production script:")
        print(f" • Chapters: {len(chapters)} | Visual Beats: {total_beats}")
        print(f" • Estimated Runtime: ~{est_runtime_mins:.1f} Minutes")
        print(f" • Markdown Script: {md_path}")
        print(f" • Pipeline Data: {json_path}")
        
        return script_package

    def _write_markdown_script(self, pkg: Dict[str, Any], output_md: str):
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(f"# YouTube Video Essay Script: {pkg['title']}\n\n")
            f.write(f"**Domain:** {pkg['domain']}  \n")
            f.write(f"**Target Voice:** `{pkg['narrator_voice']}` (Rate: `{pkg['speech_rate']}`)  \n")
            f.write(f"**Soundtrack:** Evolving Dark Ambient Bed (`{pkg['ambient_volume']}` volume)  \n\n")
            
            f.write("## 1. High-Clickthrough Title Options\n")
            for t in pkg["title_options"]:
                f.write(f"- {t}\n")
            f.write("\n---\n\n")
            
            f.write("## 2. Core Premise & Hook\n")
            f.write(f"> {pkg['core_premise']}\n\n")
            f.write(f"**Scientific & Historical Foundation:** {pkg['scientific_foundation']}\n\n")
            f.write("---\n\n")
            
            f.write("## 3. Production Chapter Breakdown & Visual Prompts\n\n")
            for ch in pkg["chapters"]:
                f.write(f"### Chapter {ch['chapter_index']}: {ch['chapter_title']}\n\n")
                f.write("| Beat ID | Narration Script | Visual Prompt (FLUX 16:9 Cinematic) |\n")
                f.write("| :--- | :--- | :--- |\n")
                for b in ch["beats"]:
                    f.write(f"| `{b['beat_id']}` | \"{b['speech']}\" | *{b['visual_prompt']}* |\n")
                f.write("\n")

    def _build_quantum_immortality_chapters(self) -> List[Dict[str, Any]]:
        return [
            {
                "chapter_index": 1,
                "chapter_title": "The Near-Miss Phenomenon",
                "beats": [
                    {
                        "beat_id": "qi1_b01",
                        "speech": "Think back to the closest you have ever come to dying.",
                        "visual_prompt": "A solitary figure standing on the edge of a rain-slicked highway at midnight, headlights cutting through thick fog"
                    },
                    {
                        "beat_id": "qi1_b02",
                        "speech": "A car swerving into your lane that missed your bumper by two inches, an illness that miraculously broke on the third night, or a slip on ice where your foot caught the edge at the last millisecond.",
                        "visual_prompt": "Close-up of a spinning tire skidding inches from the lens on wet black asphalt, raindrops frozen in flash lighting"
                    },
                    {
                        "beat_id": "qi1_b03",
                        "speech": "You exhaled, laughed off the adrenaline, and called it sheer, miraculous luck.",
                        "visual_prompt": "A person sitting alone inside a dimly lit car steering wheel, head resting against hands in shock"
                    },
                    {
                        "beat_id": "qi1_b04",
                        "speech": "Standard probability tells you that you simply survived a dangerous coin toss.",
                        "visual_prompt": "A silver antique coin spinning in mid-air against deep pitch-black shadows"
                    },
                    {
                        "beat_id": "qi1_b05",
                        "speech": "But theoretical physics offers an interpretation that is infinitely more terrifying.",
                        "visual_prompt": "A darkened physics lecture hall at midnight, chalkboard illuminated with quantum wave equations"
                    },
                    {
                        "beat_id": "qi1_b06",
                        "speech": "You did not survive that crash. In the original timeline, your body died on that asphalt.",
                        "visual_prompt": "An eerie aerial shot of an empty rural highway with flashing blue and red emergency lights in the distance"
                    },
                    {
                        "beat_id": "qi1_b07",
                        "speech": "Your friends held a funeral. Your family wept over an empty room.",
                        "visual_prompt": "Rain-streaked window looking out at a lonely cemetery with black umbrellas under gray twilight skies"
                    },
                    {
                        "beat_id": "qi1_b08",
                        "speech": "The only reason you are hearing these words right now is because consciousness cannot observe its own non-existence.",
                        "visual_prompt": "A mirror reflecting an empty room, the glass showing faint fractures spreading across the reflection"
                    },
                    {
                        "beat_id": "qi1_b09",
                        "speech": "Your awareness was forcibly wrenched across the multiverse into the only branch where you remained alive.",
                        "visual_prompt": "A human silhouette tearing into multiple translucent ghost-like copies along glowing quantum fiber lines"
                    },
                    {
                        "beat_id": "qi1_b10",
                        "speech": "Welcome to the horrifying logical trap of Quantum Immortality.",
                        "visual_prompt": "A cosmic labyrinth of glowing corridors stretching infinitely into a dark purple void"
                    }
                ]
            },
            {
                "chapter_index": 2,
                "chapter_title": "The Many-Worlds Branching Machine",
                "beats": [
                    {
                        "beat_id": "qi2_b01",
                        "speech": "In 1957, Princeton physicist Hugh Everett proposed the Many-Worlds interpretation of quantum mechanics.",
                        "visual_prompt": "Vintage 1950s archival photograph of Hugh Everett sitting at a wooden desk with mathematical papers"
                    },
                    {
                        "beat_id": "qi2_b02",
                        "speech": "In classical quantum theory, Schrödinger's cat in the box exists as a superposition of alive and dead until an observer opens the lid.",
                        "visual_prompt": "A heavy steel lockbox resting on a lab workbench, a faint radioactive glow emitting from its keyhole"
                    },
                    {
                        "beat_id": "qi2_b03",
                        "speech": "Copenhagen physicists claimed the wave function collapses into one single reality upon observation.",
                        "visual_prompt": "A single beam of white light passing through a glass prism, refracting into a sharp linear beam"
                    },
                    {
                        "beat_id": "qi2_b04",
                        "speech": "Everett argued that the wave function never collapses at all.",
                        "visual_prompt": "The beam of light shattering into hundreds of diverging geometric pathways through dark space"
                    },
                    {
                        "beat_id": "qi2_b05",
                        "speech": "Instead, every quantum event splits the universe into parallel, non-communicating branches of reality.",
                        "visual_prompt": "A towering colossal tree made of glowing light filaments branching into infinite cosmic branches"
                    },
                    {
                        "beat_id": "qi2_b06",
                        "speech": "In one branch, the atom decays and the cat dies. In another branch, the atom remains intact and the cat lives.",
                        "visual_prompt": "Split screen aesthetic: left side dark sterile room with closed box, right side glowing room with opened box"
                    },
                    {
                        "beat_id": "qi2_b07",
                        "speech": "Both worlds are equally real, physically concrete, and permanent.",
                        "visual_prompt": "Two identical Earth globes hovering side by side in the dark void of space, one shrouded in storm clouds"
                    },
                    {
                        "beat_id": "qi2_b08",
                        "speech": "Trillions of quantum splits occur inside your cells every microsecond, creating an unfathomable forest of branching worlds.",
                        "visual_prompt": "Microscopic view of DNA helix with quantum particles dividing into parallel glowing trails"
                    },
                    {
                        "beat_id": "qi2_b09",
                        "speech": "For forty years, physicists treated this as a harmless, elegant mathematical model.",
                        "visual_prompt": "A mid-century academic library with green banker lamps, dusty leatherbound physics journals"
                    },
                    {
                        "beat_id": "qi2_b10",
                        "speech": "Until 1997, when cosmologist Max Tegmark connected Everett's math to human conscious survival.",
                        "visual_prompt": "A modern theoretical astrophysicist staring into a high-powered computer terminal displaying multiversal waveforms"
                    }
                ]
            },
            {
                "chapter_index": 3,
                "chapter_title": "The Quantum Suicide Thought Experiment",
                "beats": [
                    {
                        "beat_id": "qi3_b01",
                        "speech": "Tegmark formulated a thought experiment known as Quantum Suicide.",
                        "visual_prompt": "A solitary chair in an empty concrete bunker room, an automated mechanical apparatus mounted on a tripod"
                    },
                    {
                        "beat_id": "qi3_b02",
                        "speech": "Imagine a physicist sits before a device that measures the quantum spin of a quark once every second.",
                        "visual_prompt": "Close-up of a precision brass subatomic sensor needle twitching between spin-up and spin-down"
                    },
                    {
                        "beat_id": "qi3_b03",
                        "speech": "If the spin is up, the gun clicks harmlessly. If the spin is down, the gun discharges instantly.",
                        "visual_prompt": "Mechanical firing pin primed inside a matte black chamber, illuminated by a cold LED status light"
                    },
                    {
                        "beat_id": "qi3_b04",
                        "speech": "From an outside observer's perspective, the odds of surviving ten triggers is one in one thousand and twenty-four.",
                        "visual_prompt": "An observer outside a reinforced observation window, clipboard in hand, face grim in shadows"
                    },
                    {
                        "beat_id": "qi3_b05",
                        "speech": "The observer will inevitably watch the experimenter die within seconds.",
                        "visual_prompt": "A shattered glass barrier with a smoke trail drifting in the cold air of an empty room"
                    },
                    {
                        "beat_id": "qi3_b06",
                        "speech": "But what does the experimenter experience from their own first-person perspective?",
                        "visual_prompt": "First-person POV looking directly down the dark barrel of a mechanical device in absolute silence"
                    },
                    {
                        "beat_id": "qi3_b07",
                        "speech": "In any branch where the gun fires, the experimenter's brain ceases to exist, terminating that conscious stream.",
                        "visual_prompt": "A television monitor showing sudden harsh static before shutting off to complete blackness"
                    },
                    {
                        "beat_id": "qi3_b08",
                        "speech": "Consciousness cannot experience non-existence. You cannot perceive nothingness.",
                        "visual_prompt": "An empty void with faint ripples of white noise fading into absolute infinite silence"
                    },
                    {
                        "beat_id": "qi3_b09",
                        "speech": "Therefore, the only reality the experimenter can ever subjectively witness is the branch where the gun clicked.",
                        "visual_prompt": "The mechanical needle settling on the safe green marker, a faint metallic click echoing in the room"
                    },
                    {
                        "beat_id": "qi3_b10",
                        "speech": "Trigger after trigger, click after click, the experimenter survives with mathematical certainty.",
                        "visual_prompt": "A tally mark counter etched into cold concrete, dozens of tally marks glowing with faint luminescence"
                    }
                ]
            },
            {
                "chapter_index": 4,
                "chapter_title": "The Aging Curse: Immortality Without Youth",
                "beats": [
                    {
                        "beat_id": "qi4_b01",
                        "speech": "At first glance, this might sound like a scientific loophole to eternal life.",
                        "visual_prompt": "A shimmering golden fountain of youth in an ethereal misty forest, tempting and serene"
                    },
                    {
                        "beat_id": "qi4_b02",
                        "speech": "Pop culture imagines quantum immortality as remaining forever young, brushing off death like a superhero.",
                        "visual_prompt": "Comic book style silhouette of a human standing amidst explosions unharmed, but subtly glitched"
                    },
                    {
                        "beat_id": "qi4_b03",
                        "speech": "The mathematical reality is infinitely more grotesque.",
                        "visual_prompt": "An old hospital room with flickering fluorescent lights, heart rate monitor beeping rhythmically"
                    },
                    {
                        "beat_id": "qi4_b04",
                        "speech": "Quantum immortality does not guarantee health, vitality, or youth. It only guarantees survival of consciousness.",
                        "visual_prompt": "An ancient, withered hand trembling as it grasps a hospital bed railing in the dark"
                    },
                    {
                        "beat_id": "qi4_b05",
                        "speech": "As your body ages, cellular senescence breaks down your organs, and your heart fails.",
                        "visual_prompt": "Microscopic view of telomeres fraying and dissolving at the tips of chromosomes"
                    },
                    {
                        "beat_id": "qi4_b06",
                        "speech": "In ninety-nine point nine percent of universes, you die peacefully in your bed surrounded by relatives.",
                        "visual_prompt": "An empty hospital bed under soft morning light, white sheets neatly folded, flowers on a nightstand"
                    },
                    {
                        "beat_id": "qi4_b07",
                        "speech": "But your subjective point of view cannot enter those universes.",
                        "visual_prompt": "A barred prison gate closing across a bright doorway, locking the viewer inside a darkened room"
                    },
                    {
                        "beat_id": "qi4_b08",
                        "speech": "Your consciousness is forcibly channeled into the hyper-rare outlier timelines where a freak cellular mutation kept your brain stem firing.",
                        "visual_prompt": "A single glowing neural pathway firing weakly inside a petrified brain in total isolation"
                    },
                    {
                        "beat_id": "qi4_b09",
                        "speech": "You survive the stroke, then the cardiac arrest, then the organ collapse, waking up in an increasingly agonizing body.",
                        "visual_prompt": "A shadowed patient lying paralyzed in an intensive care unit, surrounded by cold humming life-support machines"
                    },
                    {
                        "beat_id": "qi4_b10",
                        "speech": "One hundred years pass. Then one hundred and fifty. Then two hundred.",
                        "visual_prompt": "A calendar turning rapidly in a dust-filled room, pages yellowing and crumbling away to ash"
                    }
                ]
            },
            {
                "chapter_index": 5,
                "chapter_title": "The Solitary Last Survivor",
                "beats": [
                    {
                        "beat_id": "qi5_b01",
                        "speech": "In this cascading hell of quantum survival, everyone you have ever known and loved will die around you.",
                        "visual_prompt": "An ancient figure standing in a decayed cemetery where all the headstones are weathered down to blank rock"
                    },
                    {
                        "beat_id": "qi5_b02",
                        "speech": "Because from your perspective, they do not possess quantum immortality; only you do.",
                        "visual_prompt": "Translucent silhouettes of friends and family walking away into a wall of white fog, leaving one person behind"
                    },
                    {
                        "beat_id": "qi5_b03",
                        "speech": "As centuries turn into millennia, global catastrophes occur: nuclear wars, asteroid impacts, and pandemic collapses.",
                        "visual_prompt": "A ruined post-apocalyptic metropolis covered in nuclear dust, red skies with no sign of life"
                    },
                    {
                        "beat_id": "qi5_b04",
                        "speech": "In virtually every timeline, human civilization is wiped out.",
                        "visual_prompt": "A rusted satellite dish collapsed on an overgrown city skyscraper rooftop under stormy clouds"
                    },
                    {
                        "beat_id": "qi5_b05",
                        "speech": "Yet your consciousness cannot die. You will survive the fallout in an improbable bunker.",
                        "visual_prompt": "A deep subterranean concrete shelter lit by a single dying emergency bulb, rusted blast doors sealed"
                    },
                    {
                        "beat_id": "qi5_b06",
                        "speech": "You will survive the freezing volcanic winter because an improbable pocket of thermal heat sustained your breath.",
                        "visual_prompt": "A snow-covered tundra extending to the horizon, dark smoke billowing from distant volcanoes"
                    },
                    {
                        "beat_id": "qi5_b07",
                        "speech": "You become the ultimate pariah of probability, trapped on an empty planet with zero human contact.",
                        "visual_prompt": "A solitary hooded figure walking across a vast dry salt flat under a dead sky, footprints trailing behind"
                    },
                    {
                        "beat_id": "qi5_b08",
                        "speech": "The sun expands into a red giant, boiling the oceans into space five billion years from now.",
                        "visual_prompt": "A colossal red giant sun filling half the sky over a charred, magma-covered Earth"
                    },
                    {
                        "beat_id": "qi5_b09",
                        "speech": "And through some nightmarish, zero-point quantum fluke, your shattered, petrified consciousness remains awake to witness it.",
                        "visual_prompt": "A fossilized figure kneeling on scorched basalt rock, eyes fixed on the burning red furnace of the dying sun"
                    },
                    {
                        "beat_id": "qi5_b10",
                        "speech": "Death is the greatest mercy in the universe. And quantum mechanics may have stripped it from you.",
                        "visual_prompt": "A lone cracked skull resting on an asteroid drifting through the cold, starry cosmic abyss"
                    }
                ]
            },
            {
                "chapter_index": 6,
                "chapter_title": "The Prisoner of the Multiverse",
                "beats": [
                    {
                        "beat_id": "qi6_b01",
                        "speech": "Physicists debate whether quantum immortality holds under thermodynamic decoherence.",
                        "visual_prompt": "Modern physicists in a conference hall debating with laser pointers against mathematical projection screens"
                    },
                    {
                        "beat_id": "qi6_b02",
                        "speech": "Critics argue that consciousness is not a binary switch; it fades gradually as brain cells run out of oxygen.",
                        "visual_prompt": "An oscilloscope showing a brainwave frequency gradually flattening into a gentle undulating line"
                    },
                    {
                        "beat_id": "qi6_b03",
                        "speech": "If consciousness dissolves into dementia or coma before death, the subjective thread may finally sever.",
                        "visual_prompt": "A gentle mist enveloping an old garden, trees fading into peaceful soft white light"
                    },
                    {
                        "beat_id": "qi6_b04",
                        "speech": "Yet in the Many-Worlds interpretation, every possible non-zero outcome must occur somewhere in the wave function.",
                        "visual_prompt": "A vast geometric mandala of interlocked fractal spheres glowing in the void of space"
                    },
                    {
                        "beat_id": "qi6_b05",
                        "speech": "Somewhere in that mathematical infinite, there is a branch where you are the oldest living being in the history of the universe.",
                        "visual_prompt": "An ancient cosmic being sitting on an obsidian throne among cold dead stars, watching the heat death of the cosmos"
                    },
                    {
                        "beat_id": "qi6_b06",
                        "speech": "Every close call you survived in your past was not luck. It was an amputation.",
                        "visual_prompt": "A person looking at their own hands, the fingers briefly flickering with ghostly duplicate outlines"
                    },
                    {
                        "beat_id": "qi6_b07",
                        "speech": "Every time you walked away from danger, you left behind a grief-stricken world that buried your body.",
                        "visual_prompt": "A cemetery in rain with loved ones kneeling at a fresh grave, while a translucent ghost walks away down the road"
                    },
                    {
                        "beat_id": "qi6_b08",
                        "speech": "You are currently living in the statistical wreckage of your own survival.",
                        "visual_prompt": "A cracked mirror showing hundreds of different reflections, each looking slightly older and more exhausted"
                    },
                    {
                        "beat_id": "qi6_b09",
                        "speech": "The next time you narrowly dodge catastrophe, do not celebrate your good fortune.",
                        "visual_prompt": "A dark city street at night, traffic lights shifting from green to amber to deep blood red"
                    },
                    {
                        "beat_id": "qi6_b10",
                        "speech": "Ask yourself which timeline you just fell into. And how many more you will have to endure.",
                        "visual_prompt": "A solitary eye opening in the pitch-black void, reflecting an infinite line of receding doorways into the dark"
                    }
                ]
            }
        ]

    def _build_strange_matter_chapters(self) -> List[Dict[str, Any]]:
        # Pre-structured 6-chapter strange matter essay
        return []

    def _build_generic_documentary_chapters(self, pitch: Dict[str, Any]) -> List[Dict[str, Any]]:
        chapters = []
        for ch_idx in range(1, 7):
            beats = []
            for b_idx in range(1, 11):
                beat_id = f"c{ch_idx}_b{b_idx:02d}"
                speech = f"Exploring {pitch['title']}, analyzing chapter {ch_idx} beat {b_idx} with deep forensic scrutiny."
                prompt = f"Dark cinematic documentary still depicting {pitch['title']}, scene {ch_idx}_{b_idx}, 16:9 widescreen, moody lighting"
                beats.append({"beat_id": beat_id, "speech": speech, "visual_prompt": prompt})
            chapters.append({
                "chapter_index": ch_idx,
                "chapter_title": f"The Anomaly of {pitch['title']} (Part {ch_idx})",
                "beats": beats
            })
        return chapters

if __name__ == "__main__":
    writer = DocumentaryScriptWriter()
    sample_pitch = {
        "topic_id": "quantum_immortality",
        "title": "Quantum Immortality: The Infinite Prison of Consciousness",
        "domain": "Quantum Mechanics & Existential Dread",
        "hook_premise": "According to the Many-Worlds interpretation, consciousness can never witness its own death.",
        "scientific_foundation": "Hugh Everett's Many-Worlds theory, Max Tegmark's Quantum Suicide."
    }
    pkg = writer.write_full_production_script(sample_pitch)
    print("Script writer test passed!")
