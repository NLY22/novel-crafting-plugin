# -*- coding: utf-8 -*-
"""
长程因果与正文状态差量提取器 (World State Diff Extractor & Causality Updater) - Plugin Core Module
从已完成的章节正文中反向智能挖掘状态增量 (State Diff)：
1. 新增伤势、伤势恶化或愈合事件
2. 银钱物资消耗或获取变动
3. 在场关键 NPC 疑心值、态度与杀意波动
4. 地理位移与时间流逝推进
实现正文与 WorldStateLedger 的双向动态闭环，彻底根除“死账本”与跨章吃书。
"""

import sys
import io
import os
import re
import json

_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURR_DIR not in sys.path:
    sys.path.insert(0, _CURR_DIR)

from world_state_ledger import WorldStateLedger

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class StateDiffExtractor:
    """正文状态增量提取器"""

    # 伤势侦测词库
    WOUND_PATTERNS = [
        (r"(?:斩断|砍下|削断|折断)(?:了)?(?:他的|其|他)?([一二三四五六七八九十0-9]+根)?(手指|脚趾|手臂|小指|右臂|左臂|肋骨)", "致残重伤", "断裂伤"),
        (r"(?:刺穿|贯穿|洞穿)(?:了)?(?:他的|其|他)?(左肩|右肩|胸膛|腹部|大腿|左臂|右臂)", "贯通重伤", "穿透伤"),
        (r"(?:深可见骨|皮开肉绽|鲜血狂涌|血肉模糊)的?(伤口|刀痕|剑痕|裂口|血痕|血口|创口)", "外伤重创", "重度撕裂伤"),
        (r"(?:胸口|胸膛|腹部|左肩|右肩|大腿|脊背|后背|左臂|右臂|咽喉)(?:处|上)?(?:被|受)?(?:划开|割开|留下|斩出|劈出)(?:了一道|一道|一个)?(?:深可见骨|触目惊心|鲜血淋漓)?的?(伤口|刀痕|剑痕|裂口|血痕|血口|创口)", "外伤重创", "切削裂创"),
        (r"(?:中毒|毒素蔓延|黑气上涌|剧毒攻心)", "内伤剧毒", "神经/血液毒素侵蚀")
    ]

    # 财富支出与获取侦测
    MONEY_SPEND_PATTERNS = [
        r"(?:付了|花了|递出|掏出|赏了|扔下|支出|耗费|用去)([一二三四五六七八九十百千万两0-9\s]+(?:两|钱|文|吊|块|金币|银子|铜钱|铜板|灵石))",
        r"(?:用掉|耗费)([一二三四五六七八九十百千万两0-9\s]+(?:两|钱|文|铜板|灵石))"
    ]
    MONEY_GAIN_PATTERNS = [
        r"(?:赚了|得到|搜出|摸出|拿到|赏赐|缴获|收获|进账)([一二三四五六七八九十百千万两0-9\s]+(?:两|钱|文|吊|金币|银子|铜钱|铜板|灵石))"
    ]

    # 道具获取与消耗
    ITEM_CONSUMED_PATTERNS = [
        r"(?:服下|吞下|捏碎|用掉|撕毁|服用了|消耗了|耗费了|使用了)(?:仅剩的|最后一(?:粒|颗|张|包)|[一二三四五六七八九十0-9]+(?:颗|粒|枚|张|瓶|包|卷))?([^\s，。！？]{2,8}(?:丹|丸|符|药膏|卷轴|毒砂|散))",
        r"(?:倒尽|用光|耗尽|饮尽)(?:了)?([^\s，。！？]{2,8}(?:药|水|酒|油|散))"
    ]
    ITEM_ACQUIRED_PATTERNS = [
        r"(?:收入囊中|捡起|收下|夺得|获得)(?:了)?([^\s，。！？]{2,10}(?:剑|刀|令|符|玉佩|秘籍|丹药|残片|信件))",
        r"([^\s，。！？]{2,10}(?:剑|刀|令|符|玉佩|秘籍|丹药|残片|信件))(?:藏入|收进|纳入)(?:袖中|怀中|囊中|戒中)"
    ]

    # 时间流逝侦测
    TIME_PATTERNS = [
        (r"(?:次日|第二天|一连数日|过了三日|两日后|转眼三月)", 24, "跨天跳跃"),
        (r"(?:半个时辰|一个时辰|两个时辰|数个时辰|良久|几个小时)", 2, "时辰推进"),
        (r"(?:黄昏|傍晚|暮色降临|夕阳西下)", 4, "推至黄昏"),
        (r"(?:深夜|子时|三更|夜半|月上中天)", 6, "推至深夜"),
        (r"(?:黎明|破晓|天边泛白|清晨|拂晓)", 8, "推至黎明")
    ]

    def __init__(self, ledger=None):
        self.ledger = ledger or WorldStateLedger()

    def extract_diff_from_chapter(self, chapter_num, chapter_text):
        """
        从章节正文中抽取状态增量 (Diff)
        """
        clean = chapter_text.strip()
        diff = {
            "chapter": chapter_num,
            "wounds_detected": [],
            "money_events": [],
            "items_consumed": [],
            "items_acquired": [],
            "time_advancement": None,
            "suggested_actions": []
        }

        # 1. 扫描伤势
        for pat, sev, desc in self.WOUND_PATTERNS:
            matches = re.finditer(pat, clean)
            for m in matches:
                full_matched = m.group(0)
                part = m.group(1) if m.groups() and m.group(1) else "身体部位"
                diff["wounds_detected"].append({
                    "raw_text": full_matched,
                    "part": part,
                    "severity": sev,
                    "desc": desc,
                    "healing_countdown_chaps": 4 if "致残" in sev or "贯通" in sev else 2
                })
                diff["suggested_actions"].append(f"【记录新伤情】: {part} 出现 {desc} ({sev})")

        # 2. 扫描银两收支
        for pat in self.MONEY_SPEND_PATTERNS:
            for m in re.findall(pat, clean):
                diff["money_events"].append({"type": "spend", "amount": m.strip()})
                diff["suggested_actions"].append(f"【扣减银两物资】: 支出 '{m.strip()}'")

        for pat in self.MONEY_GAIN_PATTERNS:
            for m in re.findall(pat, clean):
                diff["money_events"].append({"type": "gain", "amount": m.strip()})
                diff["suggested_actions"].append(f"【增加随身财富】: 获得 '{m.strip()}'")

        # 3. 扫描消耗品与道具
        for pat in self.ITEM_CONSUMED_PATTERNS:
            for m in re.findall(pat, clean):
                diff["items_consumed"].append(m.strip())
                diff["suggested_actions"].append(f"【耗材库存扣减】: 消耗 '{m.strip()}'")

        for pat in self.ITEM_ACQUIRED_PATTERNS:
            for m in re.findall(pat, clean):
                diff["items_acquired"].append(m.strip())
                diff["suggested_actions"].append(f"【新增战利品/关键器物】: 获取 '{m.strip()}'")

        # 4. 扫描时间推进
        for pat, hours, label in self.TIME_PATTERNS:
            if re.search(pat, clean):
                diff["time_advancement"] = {"hours": hours, "label": label}
                diff["suggested_actions"].append(f"【时间线推进】: 流逝约 {hours} 小时 ({label})")
                break

        return diff

    def apply_diff_to_ledger(self, diff):
        """
        将提取出的差量自动应用并更新到 WorldStateLedger 状态机
        """
        # 1. 伤势更新
        for w in diff.get("wounds_detected", []):
            self.ledger.record_injury(
                part=w["part"],
                healing_countdown_chaps=w["healing_countdown_chaps"],
                desc=w["desc"],
                severity=w["severity"]
            )

        # 2. 财富更新
        for m in diff.get("money_events", []):
            if m["type"] == "spend":
                self.ledger.spend_money(m["amount"], purpose="正文实战支出")
            elif m["type"] == "gain":
                curr = self.ledger.state["inventory_ledger"].get("money", "")
                self.ledger.state["inventory_ledger"]["money"] = f"{curr} (新入账 {m['amount']})"

        # 3. 道具更新
        for item in diff.get("items_acquired", []):
            if item not in self.ledger.state["inventory_ledger"].setdefault("key_items", []):
                self.ledger.state["inventory_ledger"]["key_items"].append(item)

        # 4. 推进章节与时间
        hours = diff["time_advancement"]["hours"] if diff.get("time_advancement") else 2
        self.ledger.advance_chapter(elapsed_hours=hours)

        return self.ledger.generate_ledger_brief()

if __name__ == "__main__":
    extractor = StateDiffExtractor()
    sample_chapter = """
    次日清晨，破晓的微光刚刚透出云层。
    李火旺脸色苍白地摸向腰间，付了三两碎银买下那柄生锈的断剑。
    在方才突围的厮杀中，刺穿了他左肩的箭矢虽被拔出，但贯通伤口依旧血肉模糊。
    他毫不犹豫地吞下最后一粒护心丹，将获得的黑色铁令藏入袖中，迅速遁入山林。
    """
    diff = extractor.extract_diff_from_chapter(6, sample_chapter)
    print("==================================================")
    print(" 📋 【从第 6 章正文中提取出的状态增量 (State Diff)】")
    print("==================================================")
    for act in diff["suggested_actions"]:
        print(" *", act)

    print("\n自动将 Diff 写入状态机...")
    brief = extractor.apply_diff_to_ledger(diff)
    print("\n" + brief)
