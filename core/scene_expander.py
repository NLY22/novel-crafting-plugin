# -*- coding: utf-8 -*-
"""
四场次逐级渐进执笔与字数保底引擎 (Progressive Scene Expander) - Plugin Core Module
通用小说工程化工具核心生成调度器。
彻底根除单次黑盒生成导致的字数严重偏短（1200字草率收尾）与剧情摘要化快进病。
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
        1: {"name": "Scene 1: 生理承接与切入", "min_words": 600, "ideal_words": 800},
        2: {"name": "Scene 2: 多方交锋与信息差", "min_words": 800, "ideal_words": 1000},
        3: {"name": "Scene 3: 矛盾升级与行动决断", "min_words": 800, "ideal_words": 1000},
        4: {"name": "Scene 4: 悬念断章与物理硬切", "min_words": 500, "ideal_words": 700}
    }

    def __init__(self, profile_name=None):
        self.profile = load_profile(profile_name)

    def validate_scene_capacity(self, scene_id, scene_text):
        """校验单个场次的字数容量与描写深度"""
        clean = scene_text.strip()
        char_count = len(clean)
        target = self.SCENE_TARGETS.get(scene_id, {"min_words": 600, "ideal_words": 800})
        
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

if __name__ == "__main__":
    expander = SceneExpander()
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
