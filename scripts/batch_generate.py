import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_background, add_text_overlay

# 每篇文章使用跟主题直接相关的 prompt，而非通用风格模板
# 结构：masterpiece, best quality + [主体场景] + [氛围色调] + no text
# ── 文章主题分析 ──────────────────────────────────────────────────────────────
# agent-intro: ReAct 循环、多 Agent 协作、工具调用、自主规划
#   → 多个发光 AI 节点网络，信号沿连线传递，协作决策
# ai-cover-image-generator: SD 生成背景、Pillow 写字、Python 双层合成
#   → 魔法画布，代码流与彩色笔触混合涌现，创作能量
# ai-trends-2026: 推理模型、长上下文、Agent 基础设施、工程视角
#   → 未来城市夜晚，全息数据图表悬浮空中，看向远方
# mcp-intro: JSON-RPC 协议、USB-C 标准接口、Server↔Client 连接
#   → 发光接口插头与插座相连，光粒子沿数据线流动
# rag-intro: 文档分块、向量 embedding、相似度检索、知识库问答
#   → 无限数字图书馆，搜索光束从书海中精准提取一页

JOBS = [
    dict(
        title="AI Agent 工程实践",
        subtitle="从 ReAct 到多智能体协作",
        prompt=(
            "masterpiece, best quality, "
            "abstract glowing AI agent network, multiple luminous nodes connected by "
            "pulsing signal threads forming a dynamic decision graph, "
            "one central node radiating blue command light to surrounding agents, "
            "dark space background with floating circuit fragments, "
            "deep blue and electric cyan palette, volumetric glow, no text, 4k"
        ),
        output="agent-intro-cover.png",
        seed=101,
    ),
    dict(
        title="AI 封面图生成方案",
        subtitle="Tiny SD + Pillow 双层合成",
        prompt=(
            "masterpiece, best quality, "
            "magical floating canvas with colorful paint strokes emerging from flowing "
            "digital code streams, vibrant pigment splashes mixing with glowing data particles, "
            "creative energy radiating outward, "
            "warm amber orange and deep purple tones, artistic atmosphere, no text, 4k"
        ),
        output="sd-cover.png",
        seed=202,
    ),
    dict(
        title="2026 AI 技术趋势",
        subtitle="从工程视角看真正重要的变化",
        prompt=(
            "masterpiece, best quality, "
            "futuristic night cityscape with towering glass skyscrapers, "
            "holographic AI trend charts and neural network diagrams floating above rooftops, "
            "upward-rising data curves glowing in the sky, "
            "cool blue and silver neon reflections on wet streets, "
            "cinematic wide angle, dramatic atmosphere, no text, 4k"
        ),
        output="ai-trends-cover.png",
        seed=303,
    ),
    dict(
        title="MCP 协议深度解析",
        subtitle="给 AI 接上真实世界的标准接口",
        prompt=(
            "masterpiece, best quality, "
            "glowing golden connector plug precisely inserting into a futuristic port, "
            "streams of light particles flowing through the cable like data packets, "
            "surrounding circuit board patterns pulse with electric energy, "
            "deep navy blue background, electric purple and amber highlights, "
            "sharp macro focus, technological atmosphere, no text, 4k"
        ),
        output="mcp-cover.png",
        seed=404,
    ),
    dict(
        title="RAG 系统从零构建",
        subtitle="原理、实现与工程化",
        prompt=(
            "masterpiece, best quality, "
            "infinite glowing digital library extending into the horizon, "
            "thousands of luminous floating book pages arranged in geometric vector space, "
            "a single focused search beam of light extracting one radiant page from the archive, "
            "emerald green and deep teal color palette, "
            "god rays piercing through floating documents, ethereal atmosphere, no text, 4k"
        ),
        output="rag-cover.png",
        seed=505,
    ),
]


def main():
    parser = argparse.ArgumentParser(description="批量生成文章封面图")
    parser.add_argument("--repo-root", default=".", help="博客仓库根目录（默认当前目录）")
    parser.add_argument("--output-dir", default="static/articles", help="输出目录（相对 repo-root）")
    parser.add_argument("--steps", type=int, default=28, help="推理步数（默认 28）")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    out_dir = os.path.join(repo_root, args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    for i, job in enumerate(JOBS, 1):
        out_path = os.path.join(out_dir, job["output"])
        print(f"\n[{i}/{len(JOBS)}] {job['title']}")
        bg = generate_background(job["prompt"], steps=args.steps, seed=job["seed"])
        final = add_text_overlay(bg, job["title"], job["subtitle"])
        final.save(out_path)
        print(f"  -> {out_path}")

    print("\n全部完成！")


if __name__ == "__main__":
    main()
