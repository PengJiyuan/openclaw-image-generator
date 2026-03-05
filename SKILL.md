---
name: tiny-sd-cover-generator
description: Generate title-ready cover images with Tiny Stable Diffusion plus Pillow text overlay. Use this skill whenever users ask to create AI covers, regenerate visual assets, improve prompt quality, batch-generate branded thumbnails, or polish text-overlay aesthetics for blogs, docs, social posts, videos, or presentations.
---

# Tiny SD Cover Generator

Generate production-ready cover images using this pipeline:

1. Tiny Stable Diffusion generates background.
2. Pillow renders title/subtitle text only when text fields are provided.
3. The output image can be used in any system (static site, CMS, social, docs, slides).

## Trigger Conditions

Use this skill when user intent includes:

- "给文章/视频/社媒生成封面"
- "批量重生成视觉素材"
- "优化 AI 绘图 prompt"
- "Tiny SD / Stable Diffusion + Pillow"
- "标题文字和背景融合不好"

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
- Jobs file: `tiny-sd-cover-generator/scripts/jobs.example.json`
- Output directory can be any custom path.

If these paths differ, adapt commands to actual repository paths.

## Dependency Setup

Install dependencies from bundled requirements:

```bash
pip install -r tiny-sd-cover-generator/scripts/requirements.txt
```

Note: PyTorch backend auto-selects `mps`/`cuda`/`cpu` at runtime.

## Standard Workflow

### 1) Read source content and extract visual intent

For each target item, read:

- `title`
- `description`
- key bullets / headings / context text

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

Text fields are optional.

- If `title` is provided: render title (and optional subtitle).
- If `title` and `subtitle` are both missing: output background image only.

Single image command template:

```bash
python3 tiny-sd-cover-generator/scripts/generate_image.py \
  --title "<Chinese or English title>" \
  --subtitle "<optional subtitle>" \
  --prompt "<English prompt>" \
  --output "outputs/<name>.png" \
  --steps 28 \
  --seed 42 \
  --position bottom
```

Background-only template:

```bash
python3 tiny-sd-cover-generator/scripts/generate_image.py \
  --prompt "abstract flowing light ribbons, blue and cyan particles" \
  --output "outputs/background-only.png"
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
  --output "outputs/custom-cover.png"
```

### 4) Verify output quality

Inspect each generated image for:

- text readability
- panel placement
- no overflow/truncation
- style consistency across all assets

## Batch Generation Mode

When user asks to regenerate a batch of assets:

1. Prepare a jobs JSON file.
2. Draft one custom English prompt per post.
3. Set `prompt/output/seed` for each item, and add `title/subtitle` only when text overlay is needed.
4. Run:

```bash
python3 tiny-sd-cover-generator/scripts/batch_generate.py \
  --jobs tiny-sd-cover-generator/scripts/jobs.example.json
```

5. Report all generated output paths.

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
- Asset path looks wrong in your app:
  - verify actual output path and downstream config
  - use absolute or project-relative path consistently

## Response Style When Using This Skill

When executing tasks, provide:

1. Per-item one-line content summary.
2. Final English prompt used.
3. Output image path.
4. Any changed integration file paths (if any).
5. Optional seed notes for reproducibility.
