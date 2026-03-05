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

## Gallery

### Scene Types

**Wildlife Photography**

![Animal](showcase/01-animal.png)

```bash
python3 scripts/generate_image.py \
  --prompt "majestic deer standing in misty forest, golden morning light through trees, photorealistic wildlife photography, 4k" \
  --title "Wild Beauty" \
  --subtitle "大自然的精灵" \
  --output outputs/animal.png \
  --seed 101
```

---

**Automotive Photography**

![Car](showcase/02-car.png)

```bash
python3 scripts/generate_image.py \
  --prompt "sleek red sports car on winding mountain road, dramatic sunset lighting, motion blur effect, automotive photography, 4k" \
  --title "Speed & Power" \
  --subtitle "极速之美" \
  --position top \
  --output outputs/car.png \
  --seed 202
```

---

**Ocean & Beach**

![Ocean](showcase/03-ocean.png)

```bash
python3 scripts/generate_image.py \
  --prompt "turquoise ocean waves, white sandy beach, palm trees, tropical paradise, crystal clear water, landscape photography, 4k" \
  --title "Ocean Serenity" \
  --subtitle "宁静的海洋" \
  --output outputs/ocean.png \
  --seed 303
```

---

**Urban Street Photography**

![Street](showcase/04-street.png)

```bash
python3 scripts/generate_image.py \
  --prompt "busy city street at dusk, neon lights, reflections on wet pavement, people walking, urban photography, cinematic mood, 4k" \
  --title "Urban Life" \
  --subtitle "城市街头" \
  --position center \
  --output outputs/street.png \
  --seed 404
```

---

**Architecture & Real Estate**

![House](showcase/05-house.png)

```bash
python3 scripts/generate_image.py \
  --prompt "modern luxury house with large windows, sunset view, architectural design, cozy warm lighting from inside, contemporary architecture, 4k" \
  --title "Dream Home" \
  --subtitle "建筑之美" \
  --output outputs/house.png \
  --seed 505
```

---

## Usage Examples

### Basic Usage

Background image only:

```bash
python3 scripts/generate_image.py \
  --prompt "tropical beach with turquoise water, white sand, paradise island, 4k" \
  --output outputs/beach.png
```

With text overlay (default style):

```bash
python3 scripts/generate_image.py \
  --prompt "majestic lion in african savanna, golden hour, wildlife photography, 4k" \
  --title "Wildlife Photography" \
  --subtitle "Exploring Nature's Beauty" \
  --output outputs/lion.png
```

### Text Customization

Custom font size:

```bash
python3 scripts/generate_image.py \
  --prompt "minimalist geometric background, soft gradient, 4k" \
  --title "Large Title" \
  --title-size 70 \
  --subtitle-size 30 \
  --output outputs/large-text.png
```

Custom colors:

```bash
python3 scripts/generate_image.py \
  --prompt "sunset ocean waves, warm colors, 4k" \
  --title "Ocean Sunset" \
  --title-color "255,100,50,255" \
  --subtitle-color "255,200,150,255" \
  --output outputs/warm-colors.png
```

No outline (clean look):

```bash
python3 scripts/generate_image.py \
  --prompt "clean white background, minimal, 4k" \
  --title "Clean Design" \
  --outline-width 0 \
  --output outputs/no-outline.png
```

Text position options:

```bash
# Bottom (default)
python3 scripts/generate_image.py \
  --prompt "landscape scene, 4k" \
  --title "Bottom Text" \
  --position bottom \
  --output outputs/bottom.png

# Center
python3 scripts/generate_image.py \
  --prompt "symmetric composition, 4k" \
  --title "Centered" \
  --position center \
  --output outputs/center.png

# Top
python3 scripts/generate_image.py \
  --prompt "sky scene, 4k" \
  --title "Top Text" \
  --position top \
  --output outputs/top.png
```

### Generation Parameters

Control image quality:

```bash
python3 scripts/generate_image.py \
  --prompt "detailed portrait, 4k" \
  --steps 30 \
  --seed 42 \
  --output outputs/quality.png
```

- `--steps`: Inference steps (20-35 recommended, higher = better quality but slower)
- `--seed`: Random seed for reproducibility (same seed = same output)

---

## Batch Mode

Create a JSON file with multiple jobs:

```json
{
  "jobs": [
    {
      "name": "cat-portrait",
      "prompt": "cute cat on windowsill, soft light, 4k",
      "title": "Feline Grace",
      "output": "outputs/cat.png",
      "seed": 101,
      "steps": 28
    },
    {
      "name": "mountain-landscape",
      "prompt": "mountain peaks at sunrise, 4k",
      "title": "Alpine Heights",
      "subtitle": "Journey to the Summit",
      "output": "outputs/mountain.png",
      "seed": 202,
      "steps": 28,
      "position": "bottom"
    }
  ]
}
```

Run batch generation:

```bash
python3 scripts/batch_generate.py --jobs your_jobs.json
```

---

## Notes

- **Prompts must be in English** - Stable Diffusion models only understand English
- **Prompt parameter is required** - No built-in style templates
- **Text overlay is optional** - Omit `--title` to generate background only
- **Default image size**: 512×384 (4:3 ratio)
- **Color format**: `R,G,B,A` or `R,G,B` (e.g., `255,0,0,200` for semi-transparent red)
