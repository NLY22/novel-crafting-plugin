# -*- coding: utf-8 -*-
"""
跨章节“反土拨鼠之日”纵向审查器 (Longitudinal Linter & Anti-Groundhog Engine)
通用小说工程化工具 (Novel-Crafting Engine) 核心模块。
通过向量余弦相似度与时空拓扑状态机，严密拦截跨章节结构同质化与起手收口复制粘贴。
"""

import sys
import io
import os
import re
import math
from collections import Counter

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class VectorMath:
    """轻量级纯标准库 N-gram TF-IDF 与余弦相似度计算器"""
    
    @staticmethod
    def extract_ngrams(text, n=2):
        clean = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
        if len(clean) < n:
            return [clean] if clean else []
        return [clean[i:i+n] for i in range(len(clean) - n + 1)]

    @classmethod
    def cosine_similarity(cls, text1, text2):
        if not text1 or not text2:
            return 0.0
        
        ngrams1 = cls.extract_ngrams(text1, 2) + cls.extract_ngrams(text1, 3)
        ngrams2 = cls.extract_ngrams(text2, 2) + cls.extract_ngrams(text2, 3)
        
        if not ngrams1 or not ngrams2:
            return 0.0
            
        c1 = Counter(ngrams1)
        c2 = Counter(ngrams2)
        
        all_words = set(c1.keys()).union(set(c2.keys()))
        dot_product = sum(c1.get(w, 0) * c2.get(w, 0) for w in all_words)
        
        norm1 = math.sqrt(sum(v ** 2 for v in c1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in c2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)

class LongitudinalLinter:
    """跨章节纵向审计引擎 (v3.1: 搭载行为意图模式状态机，杜绝同义同构重述)"""

    # 宏观行为原型库 (Behavioral Archetypes)
    BEHAVIORAL_ARCHETYPES_OPENING = [
        {
            "id": "ARCH_DAWN_WAKE_EXIT",
            "name": "【破晓苏醒/推门打卡起手式】",
            "sememes": [
                r"(?:清晨|一早|拂晓|破晓|天边泛白|旭日|晓日|晨光|红日东升|红彤彤的|第一缕|睁开眼|醒来|睡眼惺忪|打了个哈欠|伸了个懒腰)",
                r"(?:跨出|推门|迈步|走出|下床|迈出门槛|离开房间|走向院落|走向工位|推开房门)"
            ],
            "description": "连续章节以破晓苏醒、打哈欠伸懒腰、推门下床开篇，流水账痕迹严重"
        },
        {
            "id": "ARCH_EATING_BREAKFAST",
            "name": "【琐碎早餐/进食开局】",
            "sememes": [
                r"(?:早餐|豆浆|油条|包子|面汤|馒头|灵谷|粥|干粮|茶点|早市|热气腾腾)",
                r"(?:咬了一口|咀嚼|咽下|吞咽|喝了半碗|就着|盛了|吃着)"
            ],
            "description": "连续章节以吃早饭、喝面汤等日常进食琐事开局，缺乏戏剧阻力"
        },
        {
            "id": "ARCH_DESK_PONDERING",
            "name": "【静坐工位/书案发呆】",
            "sememes": [
                r"(?:书案|书房|工位|电脑前|案牍|静室|蒲团|密室)",
                r"(?:揉着眉心|端坐|手指轻敲|盯着屏幕|凝视着玉简|发呆|沉吟不语|敲击键盘)"
            ],
            "description": "连续章节以主角在封闭书房/工位/蒲团上独自发呆思索开局"
        }
    ]

    BEHAVIORAL_ARCHETYPES_ENDING = [
        {
            "id": "ARCH_WINDOW_TEA_SIGH",
            "name": "【凭窗看夜景/抿茶叹气收口】",
            "sememes": [
                r"(?:窗外|夜色|月色|远方的天际|繁星|残阳|街景|雨夜|灯火辉煌)",
                r"(?:端起|抿了一口|抿着|握着茶盏|端起茶杯|端起酒碗|抿了抿)",
                r"(?:长长叹了一口气|吐出一口浊气|陷入了沉思|不知道未来|若有所思|幽幽叹道)"
            ],
            "description": "连续章节以看窗外夜景、抿一口茶水、叹一口气收口，属于典型 AI 机械式收尾"
        },
        {
            "id": "ARCH_BED_SLEEP_CUT",
            "name": "【上床睡觉/吹灯打卡收口】",
            "sememes": [
                r"(?:床榻|被褥|油灯|合上双眼|吹灭|熄灭|闭目|打坐入定|熄灯)",
                r"(?:一夜无话|沉沉睡去|夜色已深|明日再说|安然入睡|准备休息)"
            ],
            "description": "章节末尾以主角吹灯睡觉、躺下休息收口，缺乏断章钩子与悬念张力"
        }
    ]

    CLICHE_OPENINGS = [
        (r"(?:清晨|一早|醒来|睁开眼|阳光透过|闹钟|伸了个懒腰)", "千篇一律早晨清醒起手"),
        (r"(?:吃着|咀嚼|咬了一口|喝着|热气腾腾的早餐|食堂打卡)", "进食/早餐琐碎开局"),
        (r"(?:工位|办公室|电脑屏幕|复印机|键盘声)", "连续静态工位开局")
    ]

    CLICHE_ENDINGS = [
        (r"(?:看向窗外|望着窗外|远处的夜色|端起茶杯|抿了一口|长长舒了一口气)", "机械式看窗外/喝茶叹气收口"),
        (r"(?:陷入了沉思|不知道未来会怎样|或许.*才是|这就是.*)", "人生导师哲学感叹收口"),
        (r"(?:关上电脑|合上笔记本|伸了个懒腰|准备休息)", "机械式下班/睡前收口")
    ]

    def __init__(self, chapters_data=None):
        """
        chapters_data: list of dict, 每个元素形如:
        {
            "chapter_num": 1,
            "title": "第一章",
            "text": "正文内容...",
            "spatio_temporal": {
                "time": "早晨",
                "space": "封闭室内-工位"
            }
        }
        """
        self.chapters_data = chapters_data or []

    def add_chapter(self, chapter_num, title, text, space="公共场景", time_str="白天"):
        """向内存中追加章节"""
        self.chapters_data.append({
            "chapter_num": chapter_num,
            "title": title,
            "text": text,
            "spatio_temporal": {
                "space": space,
                "time": time_str
            }
        })

    def audit_chapter(self, chapter_num, text, space="公共场景", time_str="白天"):
        """审计单章与前章的碰撞"""
        cur_entry = {
            "chapter_num": chapter_num,
            "title": f"第{chapter_num}章",
            "text": text,
            "spatio_temporal": {
                "space": space,
                "time": time_str
            }
        }
        all_chaps = list(self.chapters_data)
        if not any(c.get("chapter_num") == chapter_num for c in all_chaps):
            all_chaps.append(cur_entry)
        temp_linter = LongitudinalLinter(all_chaps)
        head_tail = temp_linter.audit_head_tail_similarity(len(all_chaps) - 1)
        spatio = temp_linter.audit_spatio_temporal_diversity()
        warnings = []
        for r in head_tail:
            if r.get("is_violation"):
                warnings.append(r.get("fix_suggestion", "起手或收口与前章高度同质化"))
        for s in spatio:
            if s.get("is_violation"):
                warnings.append(s.get("message", "时空拓扑连续单调"))
        return {
            "passed": len(warnings) == 0,
            "warnings": warnings,
            "head_tail_reports": head_tail,
            "spatio_reports": spatio
        }

    def load_chapters_from_dir(self, drafts_dir):
        """从章节草稿目录自动按章节顺序加载"""
        self.chapters_data = []
        if not os.path.exists(drafts_dir):
            return self.chapters_data
            
        files = [f for f in os.listdir(drafts_dir) if f.endswith(".md") or f.endswith(".txt")]
        # 按文件名中的数字或章节名排序
        def sort_key(fn):
            m = re.search(r'\d+', fn)
            if m:
                return int(m.group(0))
            zh_num = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
            for k, v in zh_num.items():
                if f"第{k}" in fn:
                    return v
            return 999
            
        files.sort(key=sort_key)
        for fn in files:
            p = os.path.join(drafts_dir, fn)
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.chapters_data.append({
                "chapter_num": len(self.chapters_data) + 1,
                "title": os.path.splitext(fn)[0],
                "file_path": p,
                "text": content
            })
        return self.chapters_data

    @staticmethod
    def slice_head_and_tail(text, ratio=0.10, min_chars=120, max_chars=400):
        """提取章节起手式 (前10%) 与收口式 (后10%)"""
        clean = text.strip()
        total_len = len(clean)
        if total_len < 300:
            return clean, clean
            
        slice_len = max(min_chars, min(max_chars, int(total_len * ratio)))
        head = clean[:slice_len]
        tail = clean[-slice_len:]
        return head, tail

    def audit_head_tail_similarity(self, current_idx=None):
        """审查跨章节首尾段向量余弦碰撞 (Head/Tail Semantic Collision Detector)"""
        reports = []
        chapters = self.chapters_data
        if len(chapters) < 2:
            return reports
            
        indices_to_check = [current_idx] if current_idx is not None else range(1, len(chapters))
        
        for i in indices_to_check:
            cur = chapters[i]
            prev1 = chapters[i - 1]
            prev2 = chapters[i - 2] if i >= 2 else None
            
            cur_head, cur_tail = self.slice_head_and_tail(cur["text"])
            p1_head, p1_tail = self.slice_head_and_tail(prev1["text"])
            
            # 1. 相似度余弦检验
            head_sim_1 = VectorMath.cosine_similarity(cur_head, p1_head)
            tail_sim_1 = VectorMath.cosine_similarity(cur_tail, p1_tail)
            
            head_sim_2 = VectorMath.cosine_similarity(cur_head, self.slice_head_and_tail(prev2["text"])[0]) if prev2 else 0.0
            tail_sim_2 = VectorMath.cosine_similarity(cur_tail, self.slice_head_and_tail(prev2["text"])[1]) if prev2 else 0.0
            
            max_head_sim = max(head_sim_1, head_sim_2)
            max_tail_sim = max(tail_sim_1, tail_sim_2)
            
            # 2. 行为意图原型与套路碰撞 (同义同构重述也能精准拦截)
            head_collision = None
            for arch in self.BEHAVIORAL_ARCHETYPES_OPENING:
                cur_match = all(re.search(s, cur_head) for s in arch["sememes"])
                p1_match = all(re.search(s, p1_head) for s in arch["sememes"])
                if cur_match and p1_match:
                    head_collision = f"{arch['name']}: {arch['description']}"
                    break
            if not head_collision:
                for pat, desc in self.CLICHE_OPENINGS:
                    if re.search(pat, cur_head) and re.search(pat, p1_head):
                        head_collision = desc
                        break
                    
            tail_collision = None
            for arch in self.BEHAVIORAL_ARCHETYPES_ENDING:
                cur_match = all(re.search(s, cur_tail) for s in arch["sememes"])
                p1_match = all(re.search(s, p1_tail) for s in arch["sememes"])
                if cur_match and p1_match:
                    tail_collision = f"{arch['name']}: {arch['description']}"
                    break
            if not tail_collision:
                for pat, desc in self.CLICHE_ENDINGS:
                    if re.search(pat, cur_tail) and re.search(pat, p1_tail):
                        tail_collision = desc
                        break

            is_violation = max_head_sim >= 0.65 or max_tail_sim >= 0.65 or head_collision or tail_collision
            
            if is_violation:
                msg = (
                    f"🚨 【跨章结构同质化告警 (Structural Homogenization Error)】\n"
                    f"  * 《{cur['title']}》与前作起手式相似度: {max_head_sim:.1%} | 收口式相似度: {max_tail_sim:.1%}\n"
                    + (f"  * 起手式连续陷入套路: 【{head_collision}】！\n" if head_collision else "")
                    + (f"  * 收口式连续陷入套路: 【{tail_collision}】！\n" if tail_collision else "")
                    + f"  * 治理建议: 强制推翻当前起手/收尾，改用中途突变、对白破局或突发行动硬切！"
                )
                reports.append({
                    "is_violation": True,
                    "chapter": cur["title"],
                    "prev_chapter": prev1["title"],
                    "head_similarity": round(max_head_sim, 3),
                    "tail_similarity": round(max_tail_sim, 3),
                    "head_collision": head_collision,
                    "tail_collision": tail_collision,
                    "fix_suggestion": msg,
                    "message": msg
                })
                
        return reports

    def audit_spatio_temporal_diversity(self):
        """时空拓扑分布校验器 (Spatio-Temporal Diversity Index)"""
        warnings = []
        if len(self.chapters_data) < 3:
            return warnings

        # 简单提取空间特征关键词
        space_categories = {
            "封闭微观空间": [r"(?:办公室|工位|卧室|病房|书房|密室|牢房|洞府)"],
            "公共社交场域": [r"(?:街道|广场|酒楼|食堂|大厅|集市|擂台|会议室|网吧)"],
            "野外未知探索": [r"(?:山林|荒野|废墟|深渊|古道|河流|密林|副本)"]
        }

        history_spaces = []
        for ch in self.chapters_data:
            text = ch["text"][:1000]  # 看前一千字的主环境
            matched = "其他未知场景"
            for cat, pats in space_categories.items():
                if any(re.search(p, text) for p in pats):
                    matched = cat
                    break
            history_spaces.append((ch["title"], matched))

        # 检查是否连续 3 章发生在同一封闭微观场景
        for i in range(2, len(history_spaces)):
            c1_t, c1_s = history_spaces[i - 2]
            c2_t, c2_s = history_spaces[i - 1]
            c3_t, c3_s = history_spaces[i]
            
            if c1_s == c2_s == c3_s == "封闭微观空间":
                warnings.append({
                    "type": "空间同质化堆积",
                    "chapters": [c1_t, c2_t, c3_t],
                    "message": f"⚠️ 【空间拓扑滞涩】连续 3 章 ({c1_t} -> {c2_t} -> {c3_t}) 均局限在【封闭微观空间】！缺乏大环境交互，容易引发幽闭枯燥感，建议下一章转移至外部公共场域或未知野外。"
                })

        return warnings

    def print_longitudinal_report(self):
        """输出完整跨章节纵向审计体检报告"""
        print("=" * 65)
        print(" 🛰️  跨章节‘反土拨鼠之日’纵向审查报告 (Longitudinal Audit)")
        print(f" 📚 审计章节总数: {len(self.chapters_data)} 章")
        print("=" * 65)
        
        sim_reports = self.audit_head_tail_similarity()
        space_warnings = self.audit_spatio_temporal_diversity()
        
        if not sim_reports and not space_warnings:
            print("✅ 跨章节结构健康！未发现首尾段连续克隆或空间停滞。")
        else:
            if sim_reports:
                print(f"🛑 检出 {len(sim_reports)} 处结构同质化碰撞:")
                for r in sim_reports:
                    print(r["message"])
            if space_warnings:
                print(f"\n⚠️ 检出 {len(space_warnings)} 处时空分布滞涩:")
                for w in space_warnings:
                    print(f"  * {w['message']}")
        print("=" * 65 + "\n")
        return len(sim_reports) == 0

if __name__ == "__main__":
    ch1 = "周一早晨，阳光透过窗帘。李火旺睁开眼，从硬板床上醒来。他伸了个懒腰，走到水龙头前洗脸。今天又是平静的一天。正文开始……最后，他端起茶杯抿了一口水，看着窗外的远山，陷入了沉思。"
    ch2 = "周二清晨，闹钟响了。李火旺睁开双眼，从床上坐起身来。他深吸了一口气，拿起牙刷洗脸。正文推进……最终，李火旺合上笔记本，端起保温杯抿了一口热水，望着窗外阴沉的天空，长长舒了一口气。"
    
    linter = LongitudinalLinter([
        {"chapter_num": 1, "title": "第一章", "text": ch1},
        {"chapter_num": 2, "title": "第二章", "text": ch2}
    ])
    linter.print_longitudinal_report()
