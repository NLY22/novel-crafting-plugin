# -*- coding: utf-8 -*-
"""
长篇小说伏笔与时间锁追踪器 (Plot & Subplot Graph Tracker) - Plugin Core Module
自适应相对路径，支持自动检测宿主小说目录。
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

def find_novel_dir(start_path=None):
    """自动智能向上搜寻或定位当前小说工作区"""
    if start_path and os.path.exists(start_path):
        return start_path

    cur = os.path.abspath(start_path or os.getcwd())
    for _ in range(5):
        # 寻找包含 "故事大纲" 或 "章节草稿" 的目录
        if os.path.exists(os.path.join(cur, "故事大纲")) or os.path.exists(os.path.join(cur, "章节草稿")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    # 兜底默认路径
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "小说一"))

class PlotTracker:
    def __init__(self, novel_dir=None):
        self.novel_dir = find_novel_dir(novel_dir)
        self.outline_dir = os.path.join(self.novel_dir, "故事大纲")
        self.db_path = os.path.join(self.outline_dir, "伏笔与时间线图谱.json")
        self.md_path = os.path.join(self.outline_dir, "伏笔与时间线图谱.md")
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "timeline_current_day": "未设定",
                "subplots": []
            }

    def _save(self):
        os.makedirs(self.outline_dir, exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        rows = []
        for item in self.data["subplots"]:
            status_emoji = "🟡 待回收" if item["status"] == "pending" else "🟢 已揭晓" if item["status"] == "resolved" else "⚪ 搁置"
            rows.append(f"| {item['id']} | **{item['name']}** | 第{item['planted_chapter']}章 | 第{item.get('target_chapter', '待定')}章 | {item.get('characters', '-')} | {status_emoji} | {item.get('notes', '')} |")

        md_content = f"""# 🧵 伏笔与时间线追踪图谱

> 本文档由 `plot_tracker.py` 自动化维护与校验。
> 当前故事全局时间锚点：**{self.data.get('timeline_current_day', '未设定')}**

---

## 📌 活跃伏笔与暗线清单

| 编号 | 伏笔/暗线名称 | 埋下章节 | 建议揭晓/推进 | 涉及人物/道具 | 当前状态 | 备注与核心线索 |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
""" + "\n".join(rows) + """

---

## 💡 使用指南
- **登记新伏笔**：`python plot_tracker.py --add "伏笔名" --planted 12 --target 25 --chars "李火旺,正坤" --notes "游老爷赶大集秘密"`
- **回收伏笔**：`python plot_tracker.py --resolve 1`
- **写前提醒**：`python plot_tracker.py --due 25`
"""
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

    def add_subplot(self, name, planted_chapter, target_chapter=None, characters="", notes=""):
        new_id = len(self.data["subplots"]) + 1
        item = {
            "id": new_id,
            "name": name,
            "planted_chapter": planted_chapter,
            "target_chapter": target_chapter,
            "characters": characters,
            "status": "pending",
            "notes": notes
        }
        self.data["subplots"].append(item)
        self._save()
        print(f"✅ 成功登记伏笔 [{new_id}]《{name}》(埋于第{planted_chapter}章 -> 计划第{target_chapter}章回收)")

    def resolve_subplot(self, subplot_id, resolved_chapter, resolution_notes=""):
        for item in self.data["subplots"]:
            if item["id"] == subplot_id:
                item["status"] = "resolved"
                item["resolved_chapter"] = resolved_chapter
                if resolution_notes:
                    item["notes"] += f" [已于第{resolved_chapter}章回收: {resolution_notes}]"
                self._save()
                print(f"🎉 成功标记伏笔 [{subplot_id}]《{item['name']}》已在第{resolved_chapter}章回收！")
                return
        print(f"❌ 未找到编号为 {subplot_id} 的伏笔条目")

    def get_due_reminders(self, current_chapter):
        due_items = []
        pending_items = []
        for item in self.data["subplots"]:
            if item["status"] == "pending":
                if item.get("target_chapter") and int(item["target_chapter"]) <= int(current_chapter):
                    due_items.append(item)
                else:
                    pending_items.append(item)

        print("=" * 60)
        print(f" 🔔 【第 {current_chapter} 章】写前暗线与伏笔提醒 (工程目录: {os.path.basename(self.novel_dir)})")
        print("=" * 60)
        if due_items:
            print("🚨 【本章必须回收/推进的到期伏笔】:")
            for it in due_items:
                print(f"  * [ID {it['id']}] 《{it['name']}》（埋于第{it['planted_chapter']}章，涉及: {it['characters']}）")
                print(f"    线索说明: {it['notes']}")
        else:
            print("⚪ 本章无强制到期的硬性回收点。")

        if pending_items:
            print("\n📌 当前正在悬浮的其他长线伏笔 (可作为暗流穿插):")
            for it in pending_items[:4]:
                print(f"  * 《{it['name']}》（第{it['planted_chapter']}章，预计第{it.get('target_chapter','?')}章）")
        print("=" * 60)
        return due_items

if __name__ == "__main__":
    tracker = PlotTracker()
    tracker.get_due_reminders(15)
