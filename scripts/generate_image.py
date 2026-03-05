"""
AI 封面图生成器
流程：Tiny Stable Diffusion 生成背景  →  Pillow 写文字

用法：
  # 基本用法（仅背景图）
  python3 generate_image.py \
    --prompt "a cute cat sitting on windowsill, soft natural light, 4k" \
    --output cat.png

  # 添加文字覆盖
  python3 generate_image.py \
    --prompt "snow-capped mountain peaks at sunrise, dramatic clouds, 4k" \
    --title "Alpine Heights" \
    --subtitle "Journey to the Summit" \
    --output mountain.png

  # 自定义文字样式
  python3 generate_image.py \
    --prompt "futuristic city skyline at night, neon lights, 4k" \
    --title "Cyber City" \
    --title-size 60 \
    --title-color "0,255,255,255" \
    --outline-color "255,0,255,200" \
    --outline-width 4 \
    --position center \
    --output city.png

  # 无描边纯白文字
  python3 generate_image.py \
    --prompt "minimalist gradient background, soft colors, 4k" \
    --title "Clean Design" \
    --outline-width 0 \
    --output clean.png

  # 自定义推理参数
  python3 generate_image.py \
    --prompt "tropical beach, turquoise water, paradise, 4k" \
    --steps 30 \
    --seed 101 \
    --output beach.png
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
# 文字渲染层（纯文字，无背景效果）
# ──────────────────────────────────────────────
def add_text_overlay(
    bg: Image.Image,
    title: str,
    subtitle: str = "",
    position: str = "bottom",
    title_size: int = None,
    title_color: tuple = (255, 255, 255, 255),
    subtitle_size: int = None,
    subtitle_color: tuple = (230, 230, 230, 255),
    outline_width: int = 3,
    outline_color: tuple = (0, 0, 0, 200),
) -> Image.Image:
    W, H = bg.size
    img = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(img)

    # ── 1. 字体 & 尺寸 ──────────────────────────────
    # 标题字号：用户指定 > 自动计算
    if title_size is None:
        title_size = max(36, W // 10)
    title_font  = best_font(title, title_size)
    max_chars   = max(10, W // (title_size // 2))
    title_lines = textwrap.wrap(title, width=max_chars) or [title]
    line_h      = int(title_size * 1.3)  # 行高
    total_th    = line_h * len(title_lines)

    # 副标题字号：用户指定 > 标题的 40%
    if subtitle_size is None:
        sub_size = int(title_size * 0.4)
    else:
        sub_size = subtitle_size
    sub_font = best_font(subtitle, sub_size) if subtitle else None
    sub_h    = int(sub_size * 1.4) if subtitle else 0

    # ── 2. 计算文字块位置 ────────────────────────────
    gap = int(title_size * 0.5)  # 标题和副标题之间的间距
    total_h = total_th + (gap + sub_h if subtitle else 0)
    margin = int(H * 0.08)

    if position == "bottom":
        text_y = H - total_h - margin
    elif position == "center":
        text_y = (H - total_h) // 2
    else:  # top
        text_y = margin

    # ── 3. 渲染标题（带描边效果提升可读性）─────────
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lw = bbox[2] - bbox[0]
        x = (W - lw) // 2
        y = text_y + i * line_h
        
        # 描边效果
        if outline_width > 0:
            for ox in range(-outline_width, outline_width + 1):
                for oy in range(-outline_width, outline_width + 1):
                    if ox != 0 or oy != 0:
                        draw.text((x + ox, y + oy), line, font=title_font, fill=outline_color)
        
        # 主文字
        draw.text((x, y), line, font=title_font, fill=title_color)

    # ── 4. 渲染副标题 ──────────────────────────────
    if subtitle and sub_font:
        sub_y = text_y + total_th + gap
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sw = bbox[2] - bbox[0]
        sx = (W - sw) // 2
        
        # 副标题描边（宽度稍小）
        sub_outline_width = max(1, outline_width - 1)
        if sub_outline_width > 0:
            for ox in range(-sub_outline_width, sub_outline_width + 1):
                for oy in range(-sub_outline_width, sub_outline_width + 1):
                    if ox != 0 or oy != 0:
                        draw.text((sx + ox, sub_y + oy), subtitle, font=sub_font, fill=outline_color)
        
        # 副标题主文字
        draw.text((sx, sub_y), subtitle, font=sub_font, fill=subtitle_color)

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
    # 基本参数
    parser.add_argument("--prompt",   required=True, help="背景图 prompt (英文)")
    parser.add_argument("--title",    default="",   help="图片主标题文字 (可选)")
    parser.add_argument("--subtitle", default="",   help="副标题文字 (可选)")
    parser.add_argument("--output",   default="outputs/cover.png", help="输出路径")
    parser.add_argument("--steps",    type=int, default=28, help="推理步数 (默认 28)")
    parser.add_argument("--seed",     type=int, default=42, help="随机种子 (默认 42)")
    parser.add_argument("--position", default="bottom", choices=["bottom", "center", "top"],
                        help="文字位置 (默认 bottom)")
    
    # 文字样式参数
    parser.add_argument("--title-size", type=int, default=None, help="标题字号 (默认自动计算)")
    parser.add_argument("--title-color", default="255,255,255,255", help="标题颜色 RGBA (默认白色)")
    parser.add_argument("--subtitle-size", type=int, default=None, help="副标题字号 (默认标题的40%%)")
    parser.add_argument("--subtitle-color", default="230,230,230,255", help="副标题颜色 RGBA (默认浅灰)")
    parser.add_argument("--outline-width", type=int, default=3, help="描边宽度 (默认 3，0为无描边)")
    parser.add_argument("--outline-color", default="0,0,0,200", help="描边颜色 RGBA (默认半透明黑)")
    
    args = parser.parse_args()
    
    # 解析颜色参数
    def parse_color(color_str: str) -> tuple:
        try:
            parts = [int(x.strip()) for x in color_str.split(',')]
            if len(parts) == 3:
                return tuple(parts + [255])  # 添加默认 alpha
            elif len(parts) == 4:
                return tuple(parts)
            else:
                raise ValueError()
        except:
            print(f"⚠️  颜色格式错误: {color_str}，使用默认值")
            return (255, 255, 255, 255)
    
    title_color = parse_color(args.title_color)
    subtitle_color = parse_color(args.subtitle_color)
    outline_color = parse_color(args.outline_color)

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
        final = add_text_overlay(
            bg, title, subtitle, args.position,
            title_size=args.title_size,
            title_color=title_color,
            subtitle_size=args.subtitle_size,
            subtitle_color=subtitle_color,
            outline_width=args.outline_width,
            outline_color=outline_color
        )
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
