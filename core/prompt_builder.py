# -*- coding: utf-8 -*-
"""
名家文风技巧注入与 Few-Shot 提示词编译器 (Stylistic Prompt Builder) - Plugin Core Module
根据激活的 Profile，自动注入原著行文切片、核心手艺法则与违规禁忌，彻底杜绝 AI 假大空与文不对题。
"""

import sys
import io
import os
import json

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(PLUGIN_DIR, "profiles")

def build_style_prompt(profile_name, scene_desc, target_words=3000):
    """
    根据指定作家 Profile 编译高保真文风注入指令
    """
    # 模糊匹配 Profile
    json_path = None
    if os.path.exists(PROFILES_DIR):
        for f in os.listdir(PROFILES_DIR):
            if f.endswith(".json") and (profile_name in f or f in profile_name):
                json_path = os.path.join(PROFILES_DIR, f)
                break

    if not json_path or not os.path.exists(json_path):
        # 默认使用通用配置
        return f"【写作要求】：描写本场戏，字数目标约 {target_words} 字。要求拒绝抽象情绪，保持高对话比与长短句节奏。"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    guidance = data.get("crafting_guidance", {})
    exemplars = data.get("exemplars", {})
    metrics = data.get("metrics", {})

    prompt_lines = [
        f"==================================================================",
        f"🎯 【深度文风挂载指令】：严格仿写《{data.get('corpus_name')}》",
        f"==================================================================",
        f"【作家定位与基调】：{guidance.get('author_style', '名家风格')}",
        f"【核心语调灵魂】：{guidance.get('narrative_voice', '规范小说语调')}",
        "",
        "🛑 【绝不能犯的破坏性文风禁忌 (Violation Taboos)】："
    ]

    for fb in guidance.get("forbidden_tones", []):
        prompt_lines.append(f"  ❌ {fb}")

    prompt_lines.extend([
        "",
        "🎭 【必须贯彻的核心叙事手艺法则】:",
        f"  1. 开篇法则: {guidance.get('opening_technique', '直接切入事件')}",
        f"  2. 对白与内心: {guidance.get('internal_monologue', guidance.get('dialogue_subtext', '机锋与留白'))}",
        f"  3. 数理门禁: 对话占比需达 {metrics.get('dialogue_ratio', 0.4)*100:.0f}% 以上，长短句突发度 >= 0.55，比喻每 400 字 <= 1 个，段末 99% 硬停在动作/台词上（严禁哲理升华）。",
        "",
        "📖 【原著经典行文切片示范 (Few-Shot 语料神韵基准，请严格体会呼吸感与遣词)】:",
        "------------------------------------------------------------------"
    ])

    if exemplars.get("opening"):
        prompt_lines.append("【名家开篇示范】：")
        prompt_lines.append(exemplars["opening"])
        prompt_lines.append("")

    if exemplars.get("dialogue"):
        prompt_lines.append("【名家对白示范】：")
        prompt_lines.append(exemplars["dialogue"])
        prompt_lines.append("")

    prompt_lines.extend([
        "------------------------------------------------------------------",
        f"🎬 【本场剧情任务】: {scene_desc}",
        f"📏 【篇幅容量目标】: 严格围绕四场次推进，总字数达标 {target_words} 字，拒绝仓促快进！",
        "=================================================================="
    ])

    return "\n".join(prompt_lines)

compile_few_shot_prompt = build_style_prompt

class PromptBuilder:
    @staticmethod
    def build(profile_name, scene_desc, target_words=3000):
        return build_style_prompt(profile_name, scene_desc, target_words)

if __name__ == "__main__":
    p = build_style_prompt("顾漫", "写苗希希与孟西昂在游戏里初次相遇，组队打副本。")
    print(p)
