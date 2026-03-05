import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from generate_image import add_text_overlay, generate_background


def load_jobs(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    jobs = data.get("jobs", []) if isinstance(data, dict) else data
    if not isinstance(jobs, list):
        raise ValueError("jobs must be a list")
    return jobs


def main():
    parser = argparse.ArgumentParser(description="Batch generate cover images from JSON jobs")
    parser.add_argument("--jobs", required=True, help="Path to jobs JSON file")
    parser.add_argument("--steps", type=int, default=28, help="Inference steps (default: 28)")
    parser.add_argument("--default-position", default="bottom", choices=["bottom", "center", "top"], help="Default text position")
    args = parser.parse_args()

    jobs = load_jobs(args.jobs)
    if not jobs:
        print("No jobs found.")
        return

    total = len(jobs)
    for i, job in enumerate(jobs, 1):
        title = job.get("title", "").strip()
        subtitle = job.get("subtitle", "").strip()
        prompt = job["prompt"]
        output = job["output"]
        seed = int(job.get("seed", 42))
        position = job.get("position", args.default_position)
        item_name = title or job.get("name", f"job-{i}")

        out_dir = os.path.dirname(output) or "."
        os.makedirs(out_dir, exist_ok=True)

        print(f"\n[{i}/{total}] {item_name}")
        bg = generate_background(prompt=prompt, steps=args.steps, seed=seed)
        if title:
            final = add_text_overlay(bg=bg, title=title, subtitle=subtitle, position=position)
            print("  text overlay: on")
        elif subtitle:
            print("  text overlay: off (subtitle provided without title)")
            final = bg.convert("RGB")
        else:
            print("  text overlay: off")
            final = bg.convert("RGB")
        final.save(output)
        print(f"  -> {output}")

    print("\nDone.")


if __name__ == "__main__":
    main()
