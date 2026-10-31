# -*- coding: utf-8 -*-
"""
双层解耦通用小说生成与质检流水线 (Two-Pass Novel Pipeline) - Plugin Core Module
严格执行【Pass 1: 叙事剧力推进】与【Pass 2: 文风特征渲染】解耦。
集成微观 Universal Linter 与宏观 Longitudinal Linter 跨章纵向质检。
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
from longitudinal_linter import LongitudinalLinter
from novel_linter import NovelLinter, load_profile
from prompt_builder import build_style_prompt

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class TwoPassPipeline:
    """双层通用小说创作流水线"""

    def __init__(self, profile_name=None):
        self.narrative_engine = NarrativeEngine()
        self.profile = load_profile(profile_name)
        self.micro_linter = NovelLinter(self.profile)

    # -------------------------------------------------------------
    # PASS 1: 剧力事件骨架生成与断言
    # -------------------------------------------------------------
    def pass1_build_event_beat_sheet(self, chapter_num, chapter_title, event_card):
        """
        Pass 1: 审查并生成单章分镜事件骨架
        """
        audit = self.narrative_engine.assert_event_validity(event_card)
        markdown_card = self.narrative_engine.generate_beat_sheet_markdown(chapter_num, chapter_title, event_card)
        return {
            "passed": audit["passed"],
            "violations": audit["violations"],
            "beat_sheet_markdown": markdown_card,
            "event_card": event_card
        }

    # -------------------------------------------------------------
    # PASS 2: 文风渲染指令生成
    # -------------------------------------------------------------
    def pass2_compile_render_prompt(self, chapter_title, event_card, target_words=3200):
        """
        Pass 2: 将事件骨架输入挂载的文风 Profile，生成专属渲染指令
        """
        prof_name = self.profile.get("corpus_name", "通用名家") if self.profile else "通用名家"
        core_scene_desc = (
            f"章节: {chapter_title}\n"
            f"核心驱动大事件: {event_card.get('core_event')}\n"
            f"戏剧阻力: {event_card.get('dramatic_resistance')}\n"
            f"信息差: {event_card.get('information_gap')}\n"
            f"定格硬切点: {event_card.get('cut_point')}"
        )
        return build_style_prompt(prof_name, core_scene_desc, target_words=target_words)

    # -------------------------------------------------------------
    # 综合质检: 微观 Linter + 宏观 Longitudinal 纵向体检
    # -------------------------------------------------------------
    def run_full_audit(self, draft_text, drafts_dir=None, label="当前章节正文"):
        """
        执行双重完整质量审计
        """
        print("\n" + "=" * 65)
        print(f" 🚀  Novel-Crafting 工业级双重质量体检: {label}")
        print("=" * 65)
        
        # 1. 微观 Universal Linter
        micro_rep = self.micro_linter.lint(draft_text)
        print(f"【微观代码级 Linter】: 评分 {micro_rep['score']} 分 | 状态: {'✅ 通过' if micro_rep['passed'] else '❌ 拦截'}")
        print(f"  - 度量数据: {json.dumps(micro_rep['metrics'], ensure_ascii=False)}")
        if micro_rep['violations']:
            print("  🛑 检出违规项:")
            for v in micro_rep['violations']:
                print(f"    * {v}")
        if micro_rep['warnings']:
            print("  ⚠️ 优化警示:")
            for w in micro_rep['warnings']:
                print(f"    * {w}")

        # 2. 宏观跨章节 Longitudinal Linter
        macro_passed = True
        if drafts_dir and os.path.exists(drafts_dir):
            print("\n【宏观跨章节反土拨鼠之日审计】:")
            long_linter = LongitudinalLinter()
            long_linter.load_chapters_from_dir(drafts_dir)
            macro_passed = long_linter.print_longitudinal_report()

        total_passed = micro_rep["passed"] and macro_passed
        print("=" * 65)
        print(f"🏁 综合交付裁定: {'🟢 完美通关，准予归档' if total_passed else '🔴 存在硬伤，必须触发自愈修复'}")
        print("=" * 65 + "\n")
        return {
            "passed": total_passed,
            "micro_report": micro_rep,
            "macro_passed": macro_passed
        }

NovelPipeline = TwoPassPipeline

if __name__ == "__main__":
    pipe = TwoPassPipeline("顾漫")
    test_card = {
        "core_event": "李火旺发现料房药渣里有半块带牙印的人骨，确认丹阳子在炼人丹。",
        "dramatic_resistance": "二师兄带着巡视童子突然推门搜查药料储备，李火旺必须在一分钟内藏匿证据。",
        "information_gap": "李火旺知道了人丹真相但必须装作痴呆，二师兄疑心重重但以为李火旺只是手慢。",
        "spatio_temporal": "深夜三更 / 潮湿寒冷的清风观地下料房",
        "cut_point": "二师兄的火把光芒照在药碾子凹槽里，那半颗泛黄的牙齿正卡在石缝边沿。"
    }
    p1 = pipe.pass1_build_event_beat_sheet(5, "料房药渣", test_card)
    print("Pass 1 状态:", p1["passed"])
    p2_prompt = pipe.pass2_compile_render_prompt("料房药渣", test_card)
    print("\nPass 2 渲染指令预览:\n", p2_prompt[:400], "...")
