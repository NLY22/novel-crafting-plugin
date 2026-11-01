# -*- coding: utf-8 -*-
"""
四场次逐级渐进执笔与字数保底引擎 (Progressive Scene Expander & Multi-Turn Orchestrator) - Plugin Core Module
通用小说工程化工具核心生成调度器 (v3.1)。
通过多轮渐进式分场次执行协议 (Multi-Turn Step Protocol)，彻底根除大模型单次生成注意力衰减与 1200 字摘要化收尾病。
"""

import sys
import io
import os
import re
import json

_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURR_DIR not in sys.path:
    sys.path.insert(0, _CURR_DIR)

from narrative_engine import NarrativeEngine
from novel_linter import lint_text, load_profile

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class SceneExpander:
    """四场次物理刚性预算逐级生成器"""

    SCENE_TARGETS = {
        1: {
            "name": "Scene 1: 生理承接与冲突切入",
            "min_words": 600,
            "ideal_words": 800,
            "focus": "承接上章伤势与消耗，直接在动作准备中切入，严禁发呆洗脸叹气"
        },
        2: {
            "name": "Scene 2: 多方交锋与实质信息差",
            "min_words": 800,
            "ideal_words": 1000,
            "focus": "登场人物试探、至少3轮潜台词博弈，必须产生实质信息增量或认知反差"
        },
        3: {
            "name": "Scene 3: 矛盾升级与冒险决断",
            "min_words": 800,
            "ideal_words": 1000,
            "focus": "局势突变失衡，主角做出带有代价的决断，正面动作对抗引爆"
        },
        4: {
            "name": "Scene 4: 悬念断章与物理硬切",
            "min_words": 500,
            "ideal_words": 700,
            "focus": "局势不可逆收紧，严禁人生导师哲学感叹，定格在动作或器物异象上"
        }
    }

    def __init__(self, profile_name=None):
        self.profile = load_profile(profile_name)

    def validate_scene_capacity(self, scene_id, scene_text):
        """校验单个场次的字数容量与描写深度"""
        clean = scene_text.strip()
        char_count = len(clean)
        target = self.SCENE_TARGETS.get(scene_id, {"min_words": 600, "ideal_words": 800, "name": f"Scene {scene_id}"})
        
        passed = char_count >= target["min_words"]
        warning = None
        if not passed:
            deficit = target["min_words"] - char_count
            warning = (
                f"⚠️ 【{target['name']} 容量不足】当前仅 {char_count} 字，距离最低门禁差 {deficit} 字！\n"
                f"  * 根因诊断: 剧情推进缺乏阻力与动作链条，存在一笔带过的摘要化倾向。\n"
                f"  * 扩充抓手: 细化人物微观生理动作、增加多轮潜台词推拉、还原场景物理质感。"
            )

        return {
            "scene_id": scene_id,
            "scene_name": target["name"],
            "char_count": char_count,
            "min_words": target["min_words"],
            "passed": passed,
            "warning": warning
        }

    def stitch_chapter(self, scene_dict, chapter_title="未命名章节"):
        """
        缝合四个场次为标准长篇大章，并执行全章字数与接缝质量审查
        scene_dict: {1: "scene1文本...", 2: "scene2文本...", 3: "scene3文本...", 4: "scene4文本..."}
        """
        full_text_parts = [f"# {chapter_title}\n"]
        total_words = 0
        scene_reports = []

        for sid in [1, 2, 3, 4]:
            text = scene_dict.get(sid, "").strip()
            rep = self.validate_scene_capacity(sid, text)
            scene_reports.append(rep)
            total_words += rep["char_count"]
            full_text_parts.append(text)

        full_chapter = "\n\n".join(full_text_parts)
        is_healthy = total_words >= 2800 and all(r["passed"] for r in scene_reports)

        return {
            "full_chapter_text": full_chapter,
            "total_words": total_words,
            "is_healthy": is_healthy,
            "scene_reports": scene_reports,
            "summary": (
                f"全章总字数: {total_words} 字 | 篇幅健康度: {'🟢 达到商业大章标准 (>=2,800字)' if total_words >= 2800 else '🔴 整体偏短，需针对薄弱场次扩充'}"
            )
        }

    # -------------------------------------------------------------
    # 多轮渐进式分场次执行协议 (Multi-Turn Step Orchestrator)
    # -------------------------------------------------------------
    def get_turn_prompt(self, scene_id, scene_plan_detail, prev_scene_tail="", author_style="名家风格"):
        """
        为 AI 终端 (Claude Code / DSH / Codex) 生成单个场次的专项扩写指令
        """
        target = self.SCENE_TARGETS.get(scene_id, {"min_words": 700, "ideal_words": 900, "name": f"Scene {scene_id}", "focus": "推进剧情"})
        
        prompt_lines = [
            f"🎬 【分场专项执笔任务: {target['name']}】",
            f"--------------------------------------------------",
            f"🎯 核心聚焦: {target['focus']}",
            f"📐 本场硬性容量要求: 严格锁定在 {target['min_words']} ~ {target['ideal_words']} 字区间！",
            f"🛑 严禁越俎代庖: 【本轮仅写该场次，绝对严禁提前写后续剧情，严禁提前收尾总结！】",
            f"🎭 挂载文风: {author_style}",
            f"📋 本场具体细分动作规划: {scene_plan_detail}"
        ]

        if prev_scene_tail:
            prompt_lines.append(f"🔗 上场接缝定格 (请紧密无缝咬合该动作推进): ...{prev_scene_tail[-100:]}")

        prompt_lines.append("--------------------------------------------------")
        prompt_lines.append("✍️ 请立即输出本场次正文（无需输出标题或开场白，直接以正文行动切入）:")
        return "\n".join(prompt_lines)

if __name__ == "__main__":
    expander = SceneExpander("道诡异仙")
    print("=== 多轮分场调度指令测试 ===")
    p1 = expander.get_turn_prompt(1, "李火旺顶着寒风捣药，后脑刺痛，发现药臼底部的硬块与骨渣。")
    print(p1[:300], "...\n")
    
    sample_scenes = {
        1: "李火旺顶着寒风捣药，后脑刺痛，发现药臼底部的硬块与骨渣。" * 25,  # 约 750 字
        2: "二师兄提着铜油灯进来查账，两人带着潜台词交锋，李火旺装疯卖傻掩饰心虚。" * 30, # 约 1050 字
        3: "巡视童子打翻药筐，黑符掉出，李火旺用布满血污的手一把扣死石缝。" * 30, # 约 960 字
        4: "二师兄起疑蹲下身，手掌按在刀柄上，门外突然传来丹炉异响。" * 20  # 约 600 字
    }
    res = expander.stitch_chapter(sample_scenes, "第一章：料房残骨")
    print("缝合结果:", res["summary"])
    for s in res["scene_reports"]:
        print(f"  * {s['scene_name']}: {s['char_count']} 字 (达标: {s['passed']})")
