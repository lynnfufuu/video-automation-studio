"""
idea_generator.py - Autonomous Web-Research & YouTube Essay Ideation Agent
Acts as creative director and lead researcher for the YouTube video essay channel.
Executes:
1. Trend scanning & anomaly research (researcher.py)
2. Production-ready script drafting with title options, premise & visual prompts (script_writer.py)
3. Direct execution via CLI flags or Python imports
4. Automatic markdown export to ./youtube_essay_pipeline/scripts/
"""

import os
import sys
import argparse
import json

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add local src to path
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_ROOT = os.path.abspath(os.path.join(SRC_DIR, ".."))
sys.path.insert(0, SRC_DIR)

from researcher import DocumentaryResearcher
from script_writer import DocumentaryScriptWriter

def run_ideation_cycle(topic_query: str = None, pitch_only: bool = False) -> dict:
    print("=" * 80)
    print("🧠 [IDEA GENERATOR AGENT] YouTube Essay Research & Scriptwriting Director")
    print("Channel Style: Dark science, historical paradoxes & cosmic dread (Stickman Explains / Judicium)")
    print("=" * 80)
    
    researcher = DocumentaryResearcher()
    writer = DocumentaryScriptWriter()
    
    if pitch_only:
        print("\n🔍 Scanning trending dark anomalies and existential physics concepts...\n")
        trending = researcher.search_trending_ideas()
        for idx, t in enumerate(trending, 1):
            print(f"[{idx}] {t['title']} (Domain: {t['domain']})")
            print(f"    Hook: {t['hook_premise'][:120]}...")
            print(f"    Scores: Curiosity: {t.get('curiosity_score')}/10 | Dread: {t.get('dread_score')}/10\n")
        return {"trending_pitches": trending}
        
    # Select pitch
    if topic_query:
        print(f"\n🎯 Researching user-requested topic: '{topic_query}'...")
        pitch = researcher.select_best_pitch(topic_query)
    else:
        print("\n🌐 Autonomously selecting highest-potential trending dark science concept...")
        pitch = researcher.select_best_pitch()
        
    print(f"\n📌 Selected Concept: '{pitch['title']}'")
    print(f"   Domain: {pitch['domain']}")
    print(f"   Premise: {pitch['hook_premise']}")
    print(f"   Science: {pitch['scientific_foundation']}")
    
    # Draft production-ready script
    script_package = writer.write_full_production_script(pitch)
    
    print("\n" + "=" * 80)
    print(f"✨ [IDEATION AGENT COMPLETE] Video Concept & Production Script Ready!")
    print(f" • Script Markdown: ./youtube_essay_pipeline/scripts/{script_package['topic_id']}_script.md")
    print(f" • Ready to render with: python src/pipeline_runner.py")
    print("=" * 80)
    
    return script_package

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous YouTube Essay Ideation Agent")
    parser.add_argument("--topic", type=str, default=None, help="Target topic or paradox (e.g. 'Quantum Immortality')")
    parser.add_argument("--auto", action="store_true", help="Autonomously scan and select the best concept")
    parser.add_argument("--pitch", action="store_true", help="Display all top researched concepts without generating full script")
    
    args = parser.parse_args()
    
    if args.pitch:
        run_ideation_cycle(pitch_only=True)
    elif args.topic:
        run_ideation_cycle(topic_query=args.topic)
    else:
        # Default auto cycle
        run_ideation_cycle()
