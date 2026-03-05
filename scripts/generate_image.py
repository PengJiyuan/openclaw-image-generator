"""
AI 封面图生成器
流程：Tiny Stable Diffusion 生成背景  →  Pillow 写文字

用法：
  # 基本用法（仅背景图）
  python3 generate_image.py --prompt "a cute cat sitting on a windowsill, soft light" --output cat.png

  # 添加文字覆盖
  python3 generate_image.py \
    --title "Wildlife Photography" \
    --subtitle "Exploring Nature's Beauty" \
    --prompt "a majestic lion in african savanna, golden hour" \
    --output lion.png

  # 自定义参数
  python3 generate_image.py \
    --prompt "futuristic city skyline at night, neon lights" \
    --steps 30 \
    --seed 42 \
    --position center \
    --output city.png
"""

import argparse
import os
import textwrap

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ──────────────────────────────────────────────
# 字体路径（macOS）
# ──────────────────────────────────────────────
FONT_ZH   = "/System/Library/Fonts/PingFang.ttc"          # 中文
FONT_EN   = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"  # 英文


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in text)


def best_font(text: str, size: int) -> ImageFont.FreeTypeFont:
    return load_font(FONT_ZH if has_cjk(text) else FONT_EN, size)


# ──────────────────────────────────────────────
# 文字渲染层
# ──────────────────────────────────────────────
def add_text_overlay(
    bg: Image.Image,
    title: str,
    subtitle: str = "",
    position: str = "bottom",   # "bottom" | "center" | "top"
) -> Image.Image:
    W, H = bg.size
    img = bg.copy().convert("RGBA")

    # ── 1. 暗角晕影（四角压暗，增加景深构图感）────────
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    steps = 50
    for i in range(steps):
        alpha = int((1 - i / steps) ** 1.8 * 140)
        vd.rectangle([i, i, W - i, H - i], outline=(0, 0, 10, alpha), width=1)
    img = Image.alpha_composite(img, vignette)

    # ── 2. 字体 & 尺寸 ──────────────────────────────
    title_size  = max(30, W // 12)
    title_font  = best_font(title, title_size)
    max_chars   = max(8, W // (title_size // 2 + 2))
    title_lines = textwrap.wrap(title, width=max_chars) or [title]
    line_h      = title_size + 14
    total_th    = line_h * len(title_lines)

    sub_size = max(14, title_size - 14)
    sub_font = best_font(subtitle, sub_size) if subtitle else None
    sub_h    = sub_size + 8 if subtitle else 0

    # ── 3. 计算面板尺寸 & 位置 ────────────────────────
    pad_x    = 40
    pad_y    = 26
    accent_h = 2
    gap      = 14
    sep_gap  = 18

    inner_h  = accent_h + gap + total_th + (sep_gap + sub_h if subtitle else 0)
    panel_w  = int(W * 0.84)
    panel_h  = inner_h + pad_y * 2
    panel_x  = (W - panel_w) // 2
    margin   = int(H * 0.07)

    if position == "bottom":
        panel_y = H - panel_h - margin
    elif position == "center":
        panel_y = (H - panel_h) // 2
    else:
        panel_y = margin

    # ── 4. 真实毛玻璃：裁剪背景 → 高斯模糊 → 圆角蒙版贴回 ──
    panel_box = (panel_x, panel_y, panel_x + panel_w, panel_y + panel_h)
    bg_crop   = img.crop(panel_box).convert("RGB")
    bg_blur   = bg_crop.filter(ImageFilter.GaussianBlur(radius=10))
    # 圆角蒙版
    blur_mask = Image.new("L", (panel_w, panel_h), 0)
    ImageDraw.Draw(blur_mask).rounded_rectangle(
        [0, 0, panel_w, panel_h], radius=18, fill=255
    )
    img.paste(bg_blur.convert("RGBA"), (panel_x, panel_y), blur_mask)

    # ── 5. 面板半透明深色覆盖 + 描边 + 外投影 ──────────
    panel_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel_layer)
    # 外投影（3层扩散）
    for s in range(3, 0, -1):
        pd.rounded_rectangle(
            [panel_x - s, panel_y - s, panel_x + panel_w + s, panel_y + panel_h + s],
            radius=18 + s, outline=(0, 0, 0, 22), width=1,
        )
    # 主面板
    pd.rounded_rectangle(
        [panel_x, panel_y, panel_x + panel_w, panel_y + panel_h],
        radius=18, fill=(6, 8, 20, 150),
    )
    # 内高光描边
    pd.rounded_rectangle(
        [panel_x + 1, panel_y + 1, panel_x + panel_w - 1, panel_y + panel_h - 1],
        radius=17, outline=(255, 255, 255, 28), width=1,
    )
    img = Image.alpha_composite(img, panel_layer)
    draw = ImageDraw.Draw(img)

    # ── 6. 顶部渐变强调线（青→靛蓝，两端淡出）────────
    ax       = panel_x + pad_x + 8
    ay       = panel_y + pad_y
    line_len = panel_w - (pad_x + 8) * 2
    segs     = 60
    for s in range(segs):
        t  = s / segs
        # 颜色插值：cyan(80,200,255) → indigo(120,100,255)
        r  = int(80  + (120 - 80)  * t)
        g  = int(200 + (100 - 200) * t)
        b  = 255
        # 两端 fade（前10%和后10%渐隐）
        edge  = min(t / 0.12, 1.0, (1 - t) / 0.12)
        alpha = int(edge * 220)
        sx = ax + int(t * line_len)
        ex = ax + int((t + 1 / segs) * line_len) + 1
        draw.line([(sx, ay), (ex, ay)], fill=(r, g, b, alpha), width=2)

    # ── 7. 标题文字（5层散射阴影 + 纯白主字）─────────
    text_y = ay + accent_h + gap
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lw   = bbox[2] - bbox[0]
        x    = (W - lw) // 2
        y    = text_y + i * line_h
        # 阴影从外到内5层扩散
        shadows = [(4, 4, 45), (3, 3, 60), (2, 2, 80), (1, 2, 100), (1, 1, 130)]
        for ox, oy, a in shadows:
            draw.text((x + ox, y + oy), line, font=title_font, fill=(0, 0, 0, a))
        # 主文字
        draw.text((x, y), line, font=title_font, fill=(255, 255, 255, 255))

    # ── 8. 菱形点分隔符 + 两侧细线 + 副标题 ──────────
    if subtitle and sub_font:
        sep_y = text_y + total_th + 6
        mid_x = W // 2
        d     = 3  # 菱形半径

        # 两侧细线
        fade_len = panel_w // 5
        draw.line([(mid_x - d * 3 - fade_len, sep_y), (mid_x - d * 3, sep_y)],
                  fill=(255, 255, 255, 35), width=1)
        draw.line([(mid_x + d * 3, sep_y), (mid_x + d * 3 + fade_len, sep_y)],
                  fill=(255, 255, 255, 35), width=1)
        # 居中菱形
        draw.polygon([
            (mid_x,     sep_y - d),
            (mid_x + d, sep_y),
            (mid_x,     sep_y + d),
            (mid_x - d, sep_y),
        ], fill=(140, 195, 255, 140))

        # 副标题
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sw   = bbox[2] - bbox[0]
        sx   = (W - sw) // 2
        sy   = sep_y + d + 10
        # 副标题轻阴影
        draw.text((sx + 1, sy + 1), subtitle, font=sub_font, fill=(0, 0, 0, 80))
        draw.text((sx, sy), subtitle, font=sub_font, fill=(175, 210, 248, 200))

    return img.convert("RGB")


# ──────────────────────────────────────────────
# Negative Prompt（所有风格共用）
# 小模型必须加负面提示词，否则容易出现低质量噪点
# ──────────────────────────────────────────────
NEGATIVE_PROMPT = (
    "low quality, blurry, bad anatomy, distorted, watermark, "
    "text, logo, signature, extra fingers, deformed hands, "
    "poorly drawn, cropped, jpeg artifacts, "
    "letters, words, numbers, labels, captions"
)


# ──────────────────────────────────────────────
# Tiny SD 背景生成
# ──────────────────────────────────────────────
_PIPE = None  # 全局缓存，避免重复加载

def get_pipe():
    global _PIPE
    if _PIPE is None:
        device = "mps" if torch.backends.mps.is_available() else \
                 "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用设备: {device}")
        print("加载 Tiny SD 模型（segmind/tiny-sd）...")
        _PIPE = StableDiffusionPipeline.from_pretrained(
            "segmind/tiny-sd",
            torch_dtype=torch.float32,
        ).to(device)
        _PIPE.enable_attention_slicing()
        print("模型加载完成。")
    return _PIPE


def generate_background(prompt: str, steps: int, seed: int) -> Image.Image:
    pipe = get_pipe()
    device = pipe.device
    gen = torch.Generator(device=device).manual_seed(seed)
    print(f"生成背景中...  prompt 长度: {len(prompt)} 字符")
    result = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE_PROMPT,
        num_inference_steps=steps,
        guidance_scale=7.5,
        width=512,
        height=384,   # 4:3 比例（512×384，均为 8 的倍数）
        generator=gen,
    )
    return result.images[0]


# ──────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="AI 封面图生成器（Tiny SD + Pillow）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--prompt",   required=True, help="背景图 prompt (英文)")
    parser.add_argument("--title",    default="",   help="图片主标题文字 (可选)")
    parser.add_argument("--subtitle", default="",   help="副标题文字 (可选)")
    parser.add_argument("--output",   default="outputs/cover.png", help="输出路径")
    parser.add_argument("--steps",    type=int, default=28, help="推理步数 (默认 28)")
    parser.add_argument("--seed",     type=int, default=42, help="随机种子 (默认 42)")
    parser.add_argument("--position", default="bottom", choices=["bottom", "center", "top"],
                        help="文字位置 (默认 bottom)")
    args = parser.parse_args()

    # 检测中文：SD 模型只支持英文 prompt
    prompt = args.prompt.strip()
    if any("\u4e00" <= c <= "\u9fff" for c in prompt):
        print("⚠️  警告：检测到中文 prompt，Stable Diffusion 只理解英文。")
        print("    请将 prompt 改为英文，例如：")
        print(f"      --prompt \"a cat sitting on windowsill, soft natural light\"")
        raise SystemExit(1)
    
    print(f"使用 prompt: {prompt}")

    # 1. 生成背景
    bg = generate_background(prompt, args.steps, args.seed)

    # 2. 按需叠加文字（title/subtitle 都为空时仅输出背景图）
    title = args.title.strip()
    subtitle = args.subtitle.strip()
    if title:
        final = add_text_overlay(bg, title, subtitle, args.position)
        print("已叠加文字层。")
    elif subtitle:
        print("⚠️ 检测到 subtitle 但未提供 title，已忽略 subtitle，仅输出背景图。")
        final = bg.convert("RGB")
    else:
        print("未提供 title/subtitle，仅输出背景图。")
        final = bg.convert("RGB")

    # 3. 保存
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    final.save(args.output)
    print(f"✅ 已保存: {args.output}  ({final.size[0]}×{final.size[1]})")


if __name__ == "__main__":
    main()
