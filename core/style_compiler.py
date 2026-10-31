# -*- coding: utf-8 -*-
"""
通用小说文风编译器 (Universal Style Compiler) - Plugin Core Module
自适应相对路径，消除一切绝对路径硬编码，保证插件在任何机器、任何路径下开箱即用。
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

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROFILE_DIR = os.path.join(PLUGIN_DIR, "profiles")

def read_text_auto(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ["utf-8-sig", "utf-8", "gb18030", "gbk", "big5"]:
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="ignore")

def compile_style(corpus_path, output_dir=None, sample_chapters=40):
    if output_dir is None:
        output_dir = DEFAULT_PROFILE_DIR

    if not os.path.exists(corpus_path):
        print(f"❌ 错误: 语料文件不存在 -> {corpus_path}")
        return None

    file_name = os.path.splitext(os.path.basename(corpus_path))[0]
    print(f"🔍 正在编译语料文风: 《{file_name}》...")

    text = read_text_auto(corpus_path)

    # 智能分章抽取样本 (支持 第X章, 第X回, 第X节, Chapter X, PART X 等)
    chapters = re.split(r'\n\s*(?:第\s*[0-9一二三四五六七八九十百千]+\s*[章回节]|Chapter\s*\d+|PART\s*\d+)[^\n]*\n', text, flags=re.IGNORECASE)
    if len(chapters) > 1:
        sample_text = "\n".join(chapters[1:min(len(chapters), sample_chapters + 1)])
    else:
        sample_text = text[:300000]

    lines = [line.strip() for line in sample_text.split("\n") if line.strip()]
    total_lines = len(lines)
    total_chars = len(sample_text)

    # 1. 对话占比
    dialogue_lines = [l for l in lines if ('“' in l and '”' in l) or ('"' in l) or ('「' in l and '」' in l) or ('‘' in l and '’' in l)]
    dialogue_ratio = round(len(dialogue_lines) / total_lines, 4) if total_lines else 0

    # 2. 纯景物描写句识别
    pure_scene_patterns = [
        r"(?:夜色|天色|残阳|月光|晨曦|乌云|晚霞|日光|夕阳)",
        r"(?:冷风|狂风|夜风|微风|寒风|秋风|清风)(?:呼啸|掠过|吹|刮|拂过)",
        r"(?:小雨|暴雨|大雨|雨水|细雨)(?:淅淅沥沥|倾盆|拍打|砸|笼罩)",
        r"(?:溶洞|四周|空气|大堂|房间|走廊|街道|院落)(?:一片昏暗|昏暗无光|死一般寂静|弥漫着|静悄悄)",
        r"(?:枯树|杂草|苔藓|破庙|街灯|落叶)(?:在风中|丛生|斑驳|闪烁)"
    ]
    sentences = [s.strip() for s in re.split(r'[。！？\n]', sample_text) if s.strip()]
    scene_sentences = [
        s for s in sentences 
        if not (('“' in s and '”' in s) or ('"' in s) or ('「' in s and '」' in s)) and any(re.search(pat, s) for pat in pure_scene_patterns)
    ]
    scene_ratio = round(len(scene_sentences) / len(sentences), 4) if sentences else 0

    # 3. 比喻密度
    metaphor_pattern = re.compile(r'(?:像|宛如|仿佛|如同|似|犹如|好似)')
    metaphors = metaphor_pattern.findall(sample_text)
    metaphor_per_thousand = round((len(metaphors) / total_chars) * 1000, 2) if total_chars else 0

    # 4. 句长与突发度 (Burstiness)
    s_lens = [len(s) for s in sentences if len(s) > 1]
    avg_s_len = round(sum(s_lens) / len(s_lens), 1) if s_lens else 0
    var = sum((x - avg_s_len) ** 2 for x in s_lens) / len(s_lens) if s_lens else 0
    burstiness = round((var ** 0.5) / avg_s_len, 2) if avg_s_len else 0
    short_ratio = round(len([s for s in s_lens if s <= 12]) / len(s_lens), 4) if s_lens else 0
    long_ratio = round(len([s for s in s_lens if s >= 30]) / len(s_lens), 4) if s_lens else 0

    # 5. 结尾模式分布
    tail_action = 0
    tail_dialogue = 0
    tail_summary = 0
    valid_paras = [l for l in lines if len(l) > 10]
    for p in valid_paras:
        p_sentences = [s.strip() for s in re.split(r'[。！？]', p) if s.strip()]
        if not p_sentences:
            continue
        last_s = p_sentences[-1]
        if '”' in last_s or '"' in last_s or '」' in last_s or p.endswith('”') or p.endswith('"') or p.endswith('」'):
            tail_dialogue += 1
        elif any(w in last_s for w in ["总有", "只要", "这就是", "不仅", "终究", "或许", "才算"]):
            tail_summary += 1
        else:
            tail_action += 1
    total_p = len(valid_paras) if valid_paras else 1
    action_tail_ratio = round(tail_action / total_p, 4)
    dialogue_tail_ratio = round(tail_dialogue / total_p, 4)
    summary_tail_ratio = round(tail_summary / total_p, 4)

    # 6. 经典行文示范切片提取 (Few-Shot Exemplars)
    opening_exemplar = ""
    dialogue_exemplar = ""
    
    if len(chapters) > 1:
        c1_lines = [l.strip() for l in chapters[1].split("\n") if l.strip()]
        opening_exemplar = "\n".join(c1_lines[:10]) if c1_lines else ""
        
        # 寻找连续对白最密集的 8 行切片
        best_d_score = 0
        best_d_lines = []
        for i in range(max(0, len(c1_lines) - 8)):
            win = c1_lines[i:i+8]
            score = sum(1 for l in win if ('“' in l and '”' in l) or ('"' in l) or ('「' in l))
            if score > best_d_score:
                best_d_score = score
                best_d_lines = win
        dialogue_exemplar = "\n".join(best_d_lines) if best_d_lines else ""

    # 7. 智能提炼作家的核心写作技巧法则 (Crafting Techniques & Tropes)
    crafting_rules = {}
    if "顾漫" in file_name or "微微一笑" in file_name:
        crafting_rules = {
            "author_style": "顾漫（现代青春甜宠 / 灵动网游轻喜流）",
            "narrative_voice": "轻快灵动、网瘾少女视角、机智幽默，充满网络文化与生活化吐槽。",
            "opening_technique": "【零废话台词直接切入】：开篇第一句必须是高能对白或突发事件（如‘我们把婚离了’），绝对禁止大段天气、空调、办公室陈设等老气横秋的环境描写！",
            "internal_monologue": "【漫画式括号轻吐槽】：心理戏必须极度轻快，善用生动括号注（如‘（这孩子郁闷了就这样……）’、‘以貌取人啊！’），坚决杜绝大段沉重自省或中年伤感。",
            "dialogue_subtext": "【高段位推拉与极简留白】：台词简短、幽默、机锋极多，男女主说话充满智商在线的试探，绝不把话说透，绝不说教，绝无俗气催婚感。",
            "contrast_trope": "【强烈反差萌 (Gap Moe)】：外表艳丽不可方物 vs 游戏里扛大刀手速第一的人妖嫌疑犯；清冷从容的大神男主 vs 暗中精打细算的小心机。",
            "forbidden_tones": [
                "严禁老干部体制内公文语调（严禁写空调吹风、红头文件、副主任念材料）",
                "严禁中年相亲式报菜名（严禁写几套房、正科级、门当户对）",
                "严禁沉重、压抑、说教的人生感叹"
            ]
        }
    elif "狐尾的笔" in file_name or "道诡" in file_name:
        crafting_rules = {
            "author_style": "狐尾的笔（玄幻 / 民俗克苏鲁 / 认知失调惊悚流）",
            "narrative_voice": "神经质压迫感、真实与幻觉边界模糊、黑色幽默与深沉绝望。",
            "opening_technique": "【错乱生理现场切入】：直接将角色置于机械而诡异的动作中（如捣药、磨骨、吞药），通过周围畸形人物展现世界残酷。",
            "internal_monologue": "【真假撕裂与疑病偏执】：第一人称疯狂怀疑感官，现代精神病院的幻觉与修仙界的血肉现实剧烈交错，极度护短又疑心深重。",
            "sensory_rules": "【冷硬触觉替代抽象情绪】：绝对拦截抽象词汇，具象为‘胃酸反涌’、‘铁锈血腥味’、‘指节压碎竹简’、‘后脑刺痛’。",
            "dialogue_subtext": "【生死边缘的市井狡黠】：说话充满下层采药童子的试探与假意顺从，背地里磨刀下毒。",
            "forbidden_tones": [
                "严禁传统玄幻的装逼打脸与龙王傲慢",
                "严禁温柔阳光师兄式假大空对白",
                "严禁没有代价的凭空爆发"
            ]
        }
    elif "卖报小郎君" in file_name or "大奉" in file_name:
        crafting_rules = {
            "author_style": "卖报小郎君（仙侠修真 / 探案推理 / 市井骚话爽文流）",
            "narrative_voice": "插科打诨掩盖深谋远虑、第一人称自嘲、草蛇灰线、高段位反差装逼。",
            "opening_technique": "【生死倒计时切入】：开局必是绝境死局（监牢、充军、问斩），第一秒开始自嘲与破案求生。",
            "dialogue_subtext": "【勾栏听曲式骚话与阶级拉扯】：台词幽默荤素不忌，但与权贵博弈时骨子里极冷，善于利用律法与物理常识反咬真凶。",
            "plot_mechanics": "【微观物证反转法】：所有的伏笔都以不经意的小道具（黑符、刮痕、白磷）埋设，高潮时连环揭晓。",
            "forbidden_tones": [
                "严禁无脑跪舔权贵",
                "严禁大段空洞说明文交代设定",
                "严禁主角全知全能毫无恐惧"
            ]
        }
    else:
        crafting_rules = {
            "author_style": f"《{file_name}》风格",
            "narrative_voice": "以对话与人物摩擦力推进，拒绝环境注水与说教。",
            "opening_technique": "开门见山，直接在角色动作或对白中切入事件。",
            "dialogue_subtext": "保持言语交锋的潜台词，不直白交代背景。",
            "forbidden_tones": ["严禁空洞人生导师总结", "严禁比喻超标", "严禁慢镜头时间停滞"]
        }

    # 封装独立档案
    profile = {
        "corpus_name": file_name,
        "sample_chars": total_chars,
        "sample_lines": total_lines,
        "sample_sentences": len(sentences),
        "crafting_guidance": crafting_rules,
        "exemplars": {
            "opening": opening_exemplar,
            "dialogue": dialogue_exemplar
        },
        "metrics": {
            "dialogue_ratio": dialogue_ratio,
            "scene_ratio": scene_ratio,
            "metaphor_per_thousand": metaphor_per_thousand,
            "avg_sentence_len": avg_s_len,
            "burstiness": burstiness,
            "short_sentence_ratio": short_ratio,
            "long_sentence_ratio": long_ratio,
            "tail_distribution": {
                "action_or_abrupt": action_tail_ratio,
                "dialogue": dialogue_tail_ratio,
                "philosophical_summary": summary_tail_ratio
            }
        },
        "linter_thresholds": {
            "max_metaphors_per_400_chars": max(1, int(metaphor_per_thousand * 0.4 + 0.5)),
            "max_scene_ratio": min(0.20, max(0.08, scene_ratio * 1.5)),
            "min_burstiness": max(0.35, burstiness * 0.7),
            "prohibit_summary_ending": summary_tail_ratio < 0.05
        }
    }

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"{file_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    md_path = os.path.join(output_dir, f"{file_name}.md")
    md_content = f"""# 📑 文风独立档案：{file_name}

> 本档案由通用文风编译器自动化生成，完全独立解耦。
> 编译样本量：{total_chars:,} 字 / {total_lines:,} 行

---

## 🎭 作家灵魂技法与叙事手艺 (Core Crafting Codex)
- **风格定位**：{crafting_rules.get('author_style', '通用名家风格')}
- **语调调性**：{crafting_rules.get('narrative_voice', '规范小说调性')}
- **开篇法则**：{crafting_rules.get('opening_technique', '直接切入事件')}
- **台词与内心**：{crafting_rules.get('internal_monologue', crafting_rules.get('dialogue_subtext', '保持机锋与留白'))}

### 🚫 绝不能踩的破坏性笔调 (Forbidden Tones)
"""
    for fb in crafting_rules.get('forbidden_tones', []):
        md_content += f"- ❌ {fb}\n"

    md_content += f"""
---

## 📖 原著经典行文切片示范 (Few-Shot Exemplars)

### 1. 开篇入局示范切片：
```text
{opening_exemplar}
```

### 2. 高能对白交锋切片：
```text
{dialogue_exemplar}
```

---

## 📊 核心数理指标 (Ground Truth)
- **对话驱动占比**：{dialogue_ratio * 100:.1f}%
- **纯景物注水占比**：{scene_ratio * 100:.1f}%
- **比喻密度**：每千字 {metaphor_per_thousand} 个
- **平均单句长度**：{avg_s_len} 字
- **长短句突发度 (Burstiness)**：{burstiness} (短句占 {short_ratio*100:.1f}%, 长句占 {long_ratio*100:.1f}%)

---

## 🛑 该作家专属 Linter 门禁红线 (用于自动化静态拦截)
- **400字内比喻上限**：不得超过 **{profile['linter_thresholds']['max_metaphors_per_400_chars']}** 个
- **景物描写红线**：占比严禁超过 **{profile['linter_thresholds']['max_scene_ratio'] * 100:.1f}%**
- **结尾哲理升华拦截**：{'🔴 绝对封杀 (原著几乎为 0)' if profile['linter_thresholds']['prohibit_summary_ending'] else '⚪ 允许适量感叹'}
- **突发度底线**：≥ {profile['linter_thresholds']['min_burstiness']}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ 编译成功！已输出独立档案:")
    print(f"   - JSON 配置文件: {json_path}")
    print(f"   - Markdown 档案: {md_path}")
    return profile

class StyleCompiler:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or DEFAULT_PROFILE_DIR

    def compile(self, corpus_path, sample_chapters=40):
        return compile_style(corpus_path, self.output_dir, sample_chapters)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="一键编译小说文风为独立档案")
    parser.add_argument("--corpus", type=str, required=True, help="语料文件路径")
    parser.add_argument("--out", type=str, default=None, help="输出目录 (默认存储在插件 profiles/ 目录)")
    args = parser.parse_args()

    compile_style(args.corpus, args.out)
