# -*- coding: utf-8 -*-
"""
长程因果与世界线状态账本 (World State Ledger & Causality Tracker) - Plugin Core Module
通用小说工程化工具核心状态机。
彻底根除跨章节吃书、伤情瞬移、物资凭空出现及 NPC 仇恨/疑心失忆问题。
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

class WorldStateLedger:
    """小说长程状态与因果账本管理器"""

    def __init__(self, ledger_file=None):
        self.ledger_file = ledger_file
        self.state = {
            "current_chapter": 1,
            "timeline": {
                "day_count": 1,
                "current_time_of_day": "深夜",
                "elapsed_hours_since_last_chap": 0
            },
            "protagonist_physical": {
                "wounds": [
                    # 例如: {"part": "左肩", "desc": "刀砍贯穿伤，粗布裹扎", "severity": "重伤", "healing_countdown_chaps": 4}
                ],
                "stamina_or_energy": "精疲力竭 (刚经历死里逃生)",
                "mental_state": "高度戒备与应激"
            },
            "inventory_ledger": {
                "money": "现银三两四钱，铜钱十二文",
                "key_items": ["染血的半截黑符", "未服用的半片黑药渣"],
                "weapons": ["一柄磨损的带鞘短铁刀"],
                "consumables_remaining": "创伤药膏仅剩薄薄一层底"
            },
            "npc_relationship_matrix": {
                # 例如: "二师兄": {"suspicion_level": "极度怀疑 (85%)", "hostility": "潜藏杀心", "core_subtext": "怀疑李火旺在装疯偷药"}
            },
            "geo_location": "清风观后山地下料房"
        }
        if self.ledger_file and os.path.exists(self.ledger_file):
            self.load()

    def load(self):
        try:
            with open(self.ledger_file, "r", encoding="utf-8") as f:
                self.state = json.load(f)
        except Exception as e:
            print(f"⚠️ 读取状态账本失败: {e}")

    def save(self, output_path=None):
        p = output_path or self.ledger_file
        if not p:
            return
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def record_injury(self, part, healing_countdown_chaps=3, desc="撕裂伤", severity="重伤"):
        """记录主角生理伤情并设定愈合倒计时"""
        self.state["protagonist_physical"]["wounds"].append({
            "part": part,
            "desc": desc,
            "severity": severity,
            "healing_countdown_chaps": healing_countdown_chaps
        })

    def spend_money(self, amount, purpose=""):
        """记录花销或更新余额描述"""
        curr = self.state["inventory_ledger"].get("money", "")
        self.state["inventory_ledger"]["money"] = f"{curr} (已支出 {amount}: {purpose})"

    def update_npc_suspicion(self, npc_name, suspicion_level, core_subtext="", hostility="戒备"):
        """更新在场 NPC 的疑心与关系矩阵"""
        self.state["npc_relationship_matrix"][npc_name] = {
            "suspicion_level": f"{suspicion_level}%" if isinstance(suspicion_level, (int, float)) else str(suspicion_level),
            "hostility": hostility,
            "core_subtext": core_subtext
        }

    def generate_ledger_brief(self):
        """生成状态账本简报"""
        return self.generate_context_brief_for_pass1()

    def advance_chapter(self, elapsed_hours=2):
        """推进章节并自动消减伤势愈合倒计时"""
        self.state["current_chapter"] += 1
        self.state["timeline"]["elapsed_hours_since_last_chap"] = elapsed_hours
        remaining_wounds = []
        for w in self.state["protagonist_physical"].get("wounds", []):
            cd = w.get("healing_countdown_chaps", 1) - 1
            if cd > 0:
                w["healing_countdown_chaps"] = cd
                remaining_wounds.append(w)
        self.state["protagonist_physical"]["wounds"] = remaining_wounds

    def assert_draft_causality(self, draft_text):
        """
        因果冲突断言 (Causality Conflict Assertion)
        检查草稿中是否存在严重违背物理因果与世界账本的硬伤
        """
        violations = []
        clean = draft_text.strip()

        # 1. 生理伤情吃书检查
        for wound in self.state["protagonist_physical"].get("wounds", []):
            part = wound.get("part", "")
            severity = wound.get("severity", "")
            # 若是重伤却写剧烈动作
            if "重伤" in severity or "贯穿" in wound.get("desc", ""):
                forbidden_moves = [f"挥动{part}", f"猛推{part}", f"用{part}格挡", f"抬起{part}硬抗"]
                for fm in forbidden_moves:
                    if fm in clean:
                        violations.append(
                            f"【伤情吃书】角色【{part}】当前处于【{wound.get('desc')}】，严禁轻描淡写描写 '{fm}'！必须体现剧烈撕裂阻力与失血动作。"
                        )

        # 2. 财富与物资凭空出现检查
        money_str = self.state["inventory_ledger"].get("money", "")
        if "仅剩" in money_str or "三两" in money_str or "几文" in money_str:
            rich_spending = [r"(?:掏出|摸出|拿出|打赏)(?:一锭|两锭|十两|几十两|沉甸甸的银锭)"]
            for pat in rich_spending:
                m = re.findall(pat, clean)
                if m:
                    violations.append(
                        f"【财富凭空破产】当前账本记录仅有【{money_str}】，草稿中却出现大额支出: '{m[0]}'！必须交代银两来源或修改开销。"
                    )

        # 3. 道具消耗检查
        consumables = self.state["inventory_ledger"].get("consumables_remaining", "")
        if "仅剩" in consumables or "见底" in consumables:
            if any(w in clean for w in ["随手倒出大把药丸", "大量涂抹药膏", "毫不在意地挥霍药料"]):
                violations.append(
                    f"【消耗品透支】消耗品账本显示【{consumables}】，正文中却描写无节制使用！必须体现物资匮乏的心理煎熬。"
                )

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def generate_context_brief_for_pass1(self):
        """为 Pass 1 生成前置生理与因果约束简报"""
        lines = [
            "==================================================",
            " 📋 【因果状态机前置约束简报 (World State Ledger)】",
            "==================================================",
            f"📍 当前地理位置: {self.state.get('geo_location', '未知')}",
            f"⏳ 当前时间节点: 故事第 {self.state['timeline'].get('day_count', 1)} 天 ({self.state['timeline'].get('current_time_of_day', '未知')})",
            "🩸 主角当前生理负荷与伤情:",
        ]
        wounds = self.state["protagonist_physical"].get("wounds", [])
        if wounds:
            for w in wounds:
                lines.append(f"  * 【{w['part']}】: {w['desc']} (严重度: {w['severity']}, 预计愈合还需 {w.get('healing_countdown_chaps', '?')} 章)")
        else:
            lines.append("  * 暂无致残性重伤，但体能处于: " + self.state["protagonist_physical"].get("stamina_or_energy", "普通"))

        lines.append("🎒 随身核心物资与余银:")
        lines.append(f"  * 金钱: {self.state['inventory_ledger'].get('money')}")
        lines.append(f"  * 关键器物: {', '.join(self.state['inventory_ledger'].get('key_items', []))}")
        lines.append(f"  * 耗材储备: {self.state['inventory_ledger'].get('consumables_remaining')}")

        lines.append("👥 核心在场 NPC 疑心与仇恨度:")
        for npc, data in self.state.get("npc_relationship_matrix", {}).items():
            lines.append(f"  * {npc}: 疑心值 {data.get('suspicion_level')} | 态度: {data.get('hostility')} | 潜台词: {data.get('core_subtext')}")
        lines.append("==================================================")
        return "\n".join(lines)

if __name__ == "__main__":
    ledger = WorldStateLedger()
    ledger.state["protagonist_physical"]["wounds"].append({
        "part": "左臂",
        "desc": "深见腿骨的撕裂伤，昨夜刚敷了草药",
        "severity": "重伤",
        "healing_countdown_chaps": 3
    })
    ledger.state["inventory_ledger"]["money"] = "只剩十二文铜钱"
    print(ledger.generate_context_brief_for_pass1())
    
    test_draft = "李火旺冷笑一声，掏出一锭沉甸甸的银锭砸在桌上，随后抬起左臂硬抗了对方一铁棍。"
    audit = ledger.assert_draft_causality(test_draft)
    print("\n因果审查通过:", audit["passed"])
    for v in audit["violations"]:
        print("  -", v)
