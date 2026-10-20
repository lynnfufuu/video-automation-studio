"""
Root entry point for idea_generator.py
Allows running: python idea_generator.py [--auto | --topic "..." | --pitch]
"""
import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from idea_generator import run_ideation_cycle
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous YouTube Essay Ideation Agent")
    parser.add_argument("--topic", type=str, default=None, help="Target topic or paradox")
    parser.add_argument("--auto", action="store_true", help="Autonomously scan and select the best concept")
    parser.add_argument("--pitch", action="store_true", help="Display all top researched concepts without generating full script")
    
    args = parser.parse_args()
    
    if args.pitch:
        run_ideation_cycle(pitch_only=True)
    elif args.topic:
        run_ideation_cycle(topic_query=args.topic)
    else:
        run_ideation_cycle()
