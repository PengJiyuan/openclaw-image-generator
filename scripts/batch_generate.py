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
        
        # Text style parameters (optional)
        title_size = job.get("title_size")
        title_color = job.get("title_color")
        subtitle_size = job.get("subtitle_size")
        subtitle_color = job.get("subtitle_color")
        outline_width = job.get("outline_width", 3)
        outline_color = job.get("outline_color")

        out_dir = os.path.dirname(output) or "."
        os.makedirs(out_dir, exist_ok=True)

        print(f"\n[{i}/{total}] {item_name}")
        bg = generate_background(prompt=prompt, steps=args.steps, seed=seed)
        if title:
            # Parse color strings if provided
            if title_color and isinstance(title_color, str):
                title_color = tuple(map(int, title_color.split(',')))
            if subtitle_color and isinstance(subtitle_color, str):
                subtitle_color = tuple(map(int, subtitle_color.split(',')))
            if outline_color and isinstance(outline_color, str):
                outline_color = tuple(map(int, outline_color.split(',')))
            
            # Build kwargs for add_text_overlay
            kwargs = {"bg": bg, "title": title, "subtitle": subtitle, "position": position}
            if title_size is not None:
                kwargs["title_size"] = title_size
            if title_color is not None:
                kwargs["title_color"] = title_color
            if subtitle_size is not None:
                kwargs["subtitle_size"] = subtitle_size
            if subtitle_color is not None:
                kwargs["subtitle_color"] = subtitle_color
            if outline_width is not None:
                kwargs["outline_width"] = outline_width
            if outline_color is not None:
                kwargs["outline_color"] = outline_color
            
            final = add_text_overlay(**kwargs)
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
