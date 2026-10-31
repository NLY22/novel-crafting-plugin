# -*- coding: utf-8 -*-
"""
叙事驱动引擎 (Narrative Event Engine) - Pass 1 核心骨架生成与断言器
通用小说工程化工具 (Novel-Crafting Engine) 核心模块。
严格将【事件剧力推进】与【文风渲染】解耦，防止 AI 陷入流水账与无增量日常。
"""

import sys
import io
import os
import re
import json

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class SceneBeat:
    """四场次物理预算单个分镜节点"""
    def __init__(self, scene_id, title, target_ratio, target_words, core_function, physical_gate):
        self.scene_id = scene_id
        self.title = title
        self.target_ratio = target_ratio  # 如 0.20
        self.target_words = target_words  # 如 "600-800字"
        self.core_function = core_function
        self.physical_gate = physical_gate

    def to_dict(self):
        return {
            "scene_id": self.scene_id,
            "title": self.title,
            "target_ratio": f"{int(self.target_ratio * 100)}%",
            "target_words": self.target_words,
            "core_function": self.core_function,
            "physical_gate": self.physical_gate
        }

class NarrativeEngine:
    """Pass 1: 剧情事件骨架引擎"""

    FOUR_SCENE_BUDGET = [
        SceneBeat(
            1, "Scene 1: 生理承接与切入", 0.20, "600-800字",
            "承接上章物资消耗、地理位移与生理伤情状态，迅速以行动准备或即时动作入局。",
            "严禁慢镜头洗脸、发呆、叹气等无效动作，直接在冲突准备或行动中切入。"
        ),
        SceneBeat(
            2, "Scene 2: 多方交锋与信息差", 0.30, "900-1100字",
            "人物登场碰撞，展开至少3轮带潜台词的语言试探、利益交换或身份遮蔽。",
            "必须产生实质信息增量或认知反差，严禁一问一答的无阻力传声筒。"
        ),
        SceneBeat(
            3, "Scene 3: 矛盾升级与行动决断", 0.30, "900-1100字",
            "局势突变、第三方意外变量破坏平衡，主角被迫做出带有代价的冒险决断，正面较量引爆。",
            "必须呈现动作链条阻力与生理应激反应，严禁毫无代价的轻松碾压。"
        ),
        SceneBeat(
            4, "Scene 4: 悬念断章与物理硬切", 0.20, "500-700字",
            "局势不可逆收紧，留下深刻的悬念张力与未解谜团。",
            "拒绝人生感叹！镜头必须定格在突发异象、未发出的消息、敲门的声响、递出的物品或关键决断台词上。"
        )
    ]

    def __init__(self):
        pass

    def assert_event_validity(self, event_card):
        """
        断言校验（Assert）: 检查本章分镜事件卡是否具备实质戏剧推动力
        """
        violations = []
        
        # 1. 核心事件与改变人物处境检查
        core_event = event_card.get("core_event", "").strip()
        if len(core_event) < 15:
            violations.append("【缺乏核心大事件】本章没有明确写出改变人物处境或心理状态的核心事件（描述少于15字）。")
            
        # 2. 检查是否为平庸日常
        trivial_keywords = ["做日常", "打怪升级", "逛街买衣服", "聊聊家常", "喝咖啡闲聊", "无事发生", "平淡的一天"]
        if any(w in core_event for w in trivial_keywords):
            resistance = event_card.get("dramatic_resistance", "").strip()
            if not resistance or len(resistance) < 10:
                violations.append("【日常陷阱】本章属于过渡/日常，但未定义【戏剧阻力与信息差】。过渡章节必须有暗流或外部干扰！")

        # 3. 检查信息差与认知反差 (Information Gap)
        info_gap = event_card.get("information_gap", "").strip()
        if not info_gap or len(info_gap) < 8:
            violations.append("【缺乏信息差】未明确‘谁知道真相、谁被蒙在鼓里’的信息不对称，容易导致对话平铺直叙。")

        # 4. 检查收尾物理硬切 (Physical Cut Point)
        cut_point = event_card.get("cut_point", "").strip()
        if not cut_point:
            violations.append("【未定义收尾硬切定格点】必须指定本章末尾定格的具体动作、异象或器物。")
        elif any(w in cut_point for w in ["感叹", "顿悟", "总结", "升华", "明白道理", "思考人生"]):
            violations.append(f"【收尾硬伤】定格点出现抽象思考: '{cut_point}'。必须改为具体的物理事件或器物停顿。")

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def generate_beat_sheet_markdown(self, chapter_num, chapter_title, event_card):
        """生成标准单章分镜事件卡 Markdown 备忘"""
        lines = [
            f"# 🎬 第 {chapter_num} 章分镜事件骨架卡 (Pass 1 Event Beat Sheet)",
            f"> **章节标题**：{chapter_title}",
            f"> **篇幅目标**：2,800 ~ 3,500 字（四场次物理刚性预算）",
            "",
            "---",
            "",
            "## 🎯 核心事件动力学 (Dramatic Dynamics)",
            f"- **💥 核心驱动大事件**：{event_card.get('core_event', '待设定')}",
            f"- **⚡ 戏剧阻力与突发变量**：{event_card.get('dramatic_resistance', '待设定')}",
            f"- **🎭 信息差与认知反差**：{event_card.get('information_gap', '待设定')}",
            f"- **📍 空间场景与时间戳**：{event_card.get('spatio_temporal', '待设定')}",
            f"- **🛑 收尾物理硬切定格点**：{event_card.get('cut_point', '待设定')}",
            "",
            "---",
            "",
            "## 📐 四场次刚性预算表 (Four-Scene Budget)",
            "| 场次 | 定位与篇幅 | 核心任务 | 物理硬性门禁 | 规划剧情细目 |",
            "| :---: | :---: | :--- | :--- | :--- |"
        ]

        scenes_detail = event_card.get("scenes", {})
        for beat in self.FOUR_SCENE_BUDGET:
            s_key = f"scene_{beat.scene_id}"
            detail = scenes_detail.get(s_key, "待填写具体行动链条")
            lines.append(
                f"| **{beat.title}** | {beat.target_ratio} ({beat.target_words}) | {beat.core_function} | {beat.physical_gate} | {detail} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "> ⚠️ **流水线准则 (Pipeline Gate)**：本卡必须获得创作者确认无误后，方可输入 Pass 2 进行文风渲染编译！"
        ])
        return "\n".join(lines)

    def generate_beat_sheet(self, chapter_num, chapter_title, event_card):
        """生成分镜事件骨架并执行断言"""
        audit = self.assert_event_validity(event_card)
        md = self.generate_beat_sheet_markdown(chapter_num, chapter_title, event_card)
        return {
            "passed": audit["passed"],
            "violations": audit["violations"],
            "markdown": md,
            "chapter_num": chapter_num,
            "chapter_title": chapter_title
        }

if __name__ == "__main__":
    eng = NarrativeEngine()
    test_card = {
        "core_event": "李火旺发现料房药渣里有半块带牙印的人骨，确认丹阳子在炼人丹。",
        "dramatic_resistance": "二师兄带着巡视童子突然推门搜查药料储备，李火旺必须在一分钟内藏匿证据。",
        "information_gap": "李火旺知道了人丹真相但必须装作痴呆，二师兄疑心重重但以为李火旺只是手慢。",
        "spatio_temporal": "深夜三更 / 潮湿寒冷的清风观地下料房",
        "cut_point": "二师兄的火把光芒照在药碾子凹槽里，那半颗泛黄的牙齿正卡在石缝边沿。",
        "scenes": {
            "scene_1": "李火旺顶着寒风捣药，后脑刺痛，发现药臼底部的硬块与骨渣。",
            "scene_2": "二师兄提着铜油灯进来查账，两人带着潜台词交锋，李火旺装疯卖傻掩饰心虚。",
            "scene_3": "巡视童子打翻药筐，黑符掉出，李火旺用布满血污的手一把扣死石缝。",
            "scene_4": "二师兄起疑蹲下身，手掌按在刀柄上，门外突然传来丹炉异响。"
        }
    }
    audit = eng.assert_event_validity(test_card)
    print("断言审核通过:", audit["passed"])
    if not audit["passed"]:
        print("违规项:", audit["violations"])
    else:
        print("\n" + eng.generate_beat_sheet_markdown(5, "料房药渣", test_card))
