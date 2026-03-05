---
name: tiny-sd-cover-generator
description: Generate blog cover images with Tiny Stable Diffusion plus Pillow text overlay for Hugo posts. Use this skill whenever the user asks to make AI article covers, regenerate covers, tune prompt style, batch-generate post images, or improve text-overlay aesthetics. Prefer the bundled scripts under tiny-sd-cover-generator/scripts.
---

# Tiny SD Cover Generator

Generate production-ready article cover images using this pipeline:

1. Tiny Stable Diffusion generates background.
2. Pillow renders title/subtitle text cleanly.
3. Hugo frontmatter cover path points to generated image.

## Trigger Conditions

Use this skill when user intent includes:

- "给文章生成封面"
- "重新生成所有配图"
- "优化封面 prompt"
- "Tiny SD / Stable Diffusion + Pillow"
- "列表页封面图" or "static/articles"

## Skill Package Layout

This skill is self-contained and should be committed with this structure:

```text
tiny-sd-cover-generator/
  SKILL.md
  scripts/
    generate_image.py
    batch_generate.py
    requirements.txt
```

## Repository Assumptions

- Script path: `tiny-sd-cover-generator/scripts/generate_image.py`
- Batch helper: `tiny-sd-cover-generator/scripts/batch_generate.py`
- Output directory: `static/articles/`
- Article markdown: `content/articles/*.md`

If these paths differ, adapt commands to actual repository paths.

## Dependency Setup

Install dependencies from bundled requirements:

```bash
pip install -r tiny-sd-cover-generator/scripts/requirements.txt
```

Note: PyTorch backend auto-selects `mps`/`cuda`/`cpu` at runtime.

## Standard Workflow

### 1) Read article and extract visual intent

For each target post, read:

- `title`
- `description`
- first 2-4 section headings and key paragraphs

Then summarize in one line:

- topic noun (what it is)
- action verb (what happens)
- visual metaphor (how to depict it)
- mood/color (tone)

### 2) Translate concept into English prompt

Always write prompt in English for SD models.

Use this structure (keep concise and concrete):

`masterpiece, best quality, [main scene], [secondary detail], [lighting], [palette], [composition], no text, 4k`

Good prompt patterns for Tiny SD:

- prefer 1 clear scene over many objects
- avoid long abstract jargon chains
- keep 5-8 descriptive chunks
- include `no text, 4k`

Negative prompt is handled by the script; do not duplicate unless asked.

### 3) Generate image with text overlay

Single image command template:

```bash
python3 tiny-sd-cover-generator/scripts/generate_image.py \
  --title "<Chinese or English title>" \
  --subtitle "<optional subtitle>" \
  --prompt "<English prompt>" \
  --output "static/articles/<slug>-cover.png" \
  --steps 28 \
  --seed 42 \
  --position bottom
```

Default tuning:

- `steps`: 25-30 for Tiny SD quality/speed balance
- `seed`: fixed seed for reproducibility
- `position`: `bottom` unless background center is empty

Quick test:

```bash
python3 tiny-sd-cover-generator/scripts/generate_image.py \
  --title "Hello" \
  --prompt "abstract data flow, glowing particles" \
  --output "static/articles/custom-cover.png"
```

### 4) Update frontmatter cover block

Ensure each post has:

```yaml
cover:
  image: "/articles/<slug>-cover.png"
  alt: "<title short text>"
  caption: "由 Tiny Stable Diffusion 生成"
```

### 5) Verify quickly

Run Hugo build check:

```bash
hugo --minify
```

If preview server runs, inspect list page and article page for:

- text readability
- panel placement
- no overflow/truncation
- style consistency across covers

## Batch Generation Mode

When user asks to regenerate all article covers:

1. Read each target post.
2. Draft one custom English prompt per post.
3. Edit `tiny-sd-cover-generator/scripts/batch_generate.py` jobs list with per-article prompt + seed.
4. Run:

```bash
python3 tiny-sd-cover-generator/scripts/batch_generate.py --repo-root . --output-dir static/articles
```

5. Report outputs generated under `static/articles/`.

## Prompt Quality Rules

Do:

- concrete nouns: `city skyline`, `connector plug`, `digital library`
- strong light words: `volumetric light`, `glowing`, `cinematic`
- controlled palettes: `deep blue and cyan`, `emerald and teal`

Avoid:

- Chinese prompt text for SD
- too many unrelated objects
- conflicting styles in one prompt
- asking model to draw readable text

## Troubleshooting

- Prompt ignored / subject missing:
  - shorten prompt and move main subject to first chunk
  - increase steps to `30`
  - try 2-3 seeds (`42`, `101`, `202`)
- Text overlay looks detached:
  - keep `--position bottom`
  - adjust subtitle length
  - regenerate with calmer background prompt
- Build is fine but cover not visible:
  - check `cover.image` uses `/articles/...`
  - confirm file exists in `static/articles/`

## Response Style When Using This Skill

When executing tasks, provide:

1. Per-article one-line content summary.
2. Final English prompt used.
3. Output image path.
4. Any changed frontmatter file paths.
5. Optional seed notes for reproducibility.
