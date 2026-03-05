# tiny-sd-cover-generator

Universal Tiny SD + Pillow cover image generator skill.

This repository is not tied to Hugo. You can use it for:
- blog covers
- social media thumbnails
- documentation headers
- video cover images
- slide title cards

## Structure

```text
tiny-sd-cover-generator/
	SKILL.md
	scripts/
		generate_image.py
		batch_generate.py
		jobs.example.json
		requirements.txt
```

## Install

```bash
pip install -r scripts/requirements.txt
```

## Single Image

```bash
python3 scripts/generate_image.py \
	--title "AI Agent Engineering" \
	--subtitle "From ReAct to Multi-Agent" \
	--prompt "abstract glowing AI network, blue and cyan particles" \
	--output "outputs/agent-cover.png" \
	--steps 28 \
	--seed 42
```

`--title` and `--subtitle` are optional.

- With `--title`: generates image + text overlay.
- Without `--title`: generates background image only.

Background-only example:

```bash
python3 scripts/generate_image.py \
	--prompt "abstract flowing light ribbons, blue and cyan particles" \
	--output "outputs/background-only.png"
```

## Batch Mode

Edit `scripts/jobs.example.json`, then run:

```bash
python3 scripts/batch_generate.py --jobs scripts/jobs.example.json
```

## Notes

- Prompts should be in English for Stable Diffusion models.
- `generate_image.py` auto-adds quality prefix and `no text, 4k` suffix for custom prompts.
- The script draws text via Pillow, not the diffusion model, to ensure readable titles.
