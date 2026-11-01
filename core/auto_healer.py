# -*- coding: utf-8 -*-
"""
代码级文本定向自愈修复器 (Novel Auto-Healer & Style Purifier) - Plugin Core Module
通用小说工程化工具核心自愈引擎 (v3.1)。
具备多变体生理代换池（杜绝咬后槽牙次生同质化）与面向 AI Agent 的局域语境精准重写提示词生成能力。
"""

import sys
import io
import os
import re
import json

_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURR_DIR not in sys.path:
    sys.path.insert(0, _CURR_DIR)

from novel_linter import lint_text, load_profile

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class AutoHealer:
    """去 AI 味代码级文本自愈修复器 (支持多变体动态轮换与语境重写)"""

    # 抽象情绪多变体动态物理代换池 (按语境与出现频次动态轮转，杜绝单一替换套路)
    DYNAMIC_EMOTION_POOLS = [
        {
            "pattern": r"钻心[的的]痛|痛[，,]\s*钻心[的的]痛|钻心之痛",
            "category": "剧痛神经反射",
            "variants": [
                "后槽牙死死咬破口腔内软肉，血腥味瞬间涌上舌尖",
                "整截臂膀的肌肉猝然绷成硬铁，冷汗顺着下颌线滑落下来",
                "剧痛沿着神经根狠狠向上钻凿，疼得他呼吸骤然受阻",
                "眼角肌肉剧烈抽搐了几下，垂在身侧的指节捏得毫无血色"
            ]
        },
        {
            "pattern": r"痛彻心扉",
            "category": "深层剧痛",
            "variants": [
                "疼得整截脊椎骨剧烈抽搐了一下",
                "胸口发闷发紧，每一次吸气都像是在吞咽碎玻璃碴",
                "半边身子瞬间麻木，只剩下骨节深处酸腐的抽痛"
            ]
        },
        {
            "pattern": r"心中一紧|心头一紧|心头猛然一紧",
            "category": "突发应激紧张",
            "variants": [
                "按在袖口里的五指骤然扣紧",
                "后背贴着的湿冷衣料瞬间被一层冷汗浸透",
                "喉结上下狠狠滚动了一下，原本迈出的步子硬生生悬在半空",
                "搭在刀柄上的食指微不可察地绷直了半分"
            ]
        },
        {
            "pattern": r"心中一震|心中大骇|心头大震",
            "category": "惊骇震颤",
            "variants": [
                "后颈的汗毛根根倒竖起来",
                "脑子里轰然空了一拍，视线死死冻结在原地",
                "下颚骨不自觉地收紧，全身重心下沉随时准备暴起"
            ]
        },
        {
            "pattern": r"咯噔一下|心头咯噔",
            "category": "警惕心跳停滞",
            "variants": [
                "心跳骤然漏了一拍，呼吸猛地一滞",
                "原本平缓的鼻息猝然被掐断在喉咙口",
                "胸腔深处猛烈撞击了一下肋骨"
            ]
        },
        {
            "pattern": r"倒吸(?:一[口把]|凉气)",
            "category": "冷气与抽气",
            "variants": [
                "喉头发出极轻的咔哒一声窒息轻响",
                "牙关骤然咬死，鼻翼剧烈翕动了一下",
                "下意识往后撤了半步，浑身骨架崩紧"
            ]
        },
        {
            "pattern": r"瞳孔(?:骤缩|剧烈收缩)",
            "category": "视线定格聚焦",
            "variants": [
                "视线瞬间死死钉在对方的指节上",
                "眼皮骤然压低，目光如刀刃般锁死对方微动的指尖",
                "余光猛地凝固，眼球周围的细小血管暴跳"
            ]
        },
        {
            "pattern": r"骇然失色|骇然",
            "category": "失色外貌",
            "variants": [
                "脸色肉眼可见地刷白下来",
                "面皮微抽，原本红润的唇色瞬间褪得干干净净",
                "喉咙像被人生生扼住，半点声音都卡在气管里"
            ]
        },
        {
            "pattern": r"眼前一阵发黑|眼前一黑",
            "category": "眩晕与失衡",
            "variants": [
                "脚下猛然打了个趔趄，手掌死死撑住冰冷的砖墙",
                "胃里一阵翻江倒海般的酸水狂涌，太阳穴突突狂跳",
                "耳道里嗡的一声尖鸣，周围的声响瞬间变得空旷遥远"
            ]
        },
        {
            "pattern": r"杀意凛然|眼中闪过杀意",
            "category": "敌意动作化",
            "variants": [
                "说话的调门陡然压低了半寸，目光冷得像结了霜",
                "刀鞘内的簧片发出极轻的一声机括咬合轻响",
                "原本松弛的下巴缓缓抬起，视线直勾勾锁住对方的脖颈咽喉"
            ]
        },
        {
            "pattern": r"嘴角勾起(?:一抹)?(?:弧度|冷笑)",
            "category": "面部机械表情",
            "variants": [
                "嘴角牵起一丝僵硬冰冷的弧线",
                "半边脸颊的皮肉抽了抽，挤出一个似笑非笑的褶皱",
                "眼神丝毫未动，只是唇缝间吐出一口沉闷的浊气"
            ]
        }
    ]

    # 陈词滥调比喻物理剔除与精炼
    CLICHE_METAPHOR_FIXES = [
        (r"像一?[把座只群个]?生锈的?.*冰锥(?:一般)?", "冰冷而粗粝"),
        (r"如大山一般沉重|像大山一样沉重", "沉重得让人骨节发脆"),
        (r"像断了线的风筝", "失控地凌空倒栽下来"),
        (r"如同决堤的洪水", "瞬间倾泻而出")
    ]

    # 公文冗余病句式清洗
    BUREAUCRATIC_FIXES = [
        (r"进行了?(?:一次)?缜密的思考", "在心里飞速盘算"),
        (r"进行了?(?:仔细的)?观察", "眯起眼打量"),
        (r"进行了?(?:快速的)?包扎", "扯下布条勒紧伤口"),
        (r"不可否认的是[，,]?", ""),
        (r"毫无疑问[，,]?", ""),
        (r"在无形之中", "")
    ]

    # 结尾人生导师升华物理硬切备选池 (动态轮换器物动作)
    HARD_CUT_ENDINGS = [
        "门外传来更夫沉闷的铜锣声，一下接着一下，渐行渐远。",
        "他反手插上门闩，铜锁舌咔哒一声咬死，屋里重归死寂。",
        "灶膛里的最后一点火星扑哧暗了下去，空气里只剩下焦糊的松烟气。",
        "他没再回头，伸手将衣领往上拽了拽，快步拐进了逼仄的雨巷。",
        "桌案上的油灯芯炸开一朵焦黑的灯花，烛泪无声淌落凝固在木纹里。",
        "屋檐下的雨水积连成线，啪嗒一声砸在阶前青石板的凹槽中。"
    ]

    def __init__(self, profile=None):
        self.profile = profile
        self._counter_map = {}

    def _get_next_variant(self, pattern_key, variants):
        idx = self._counter_map.get(pattern_key, 0)
        chosen = variants[idx % len(variants)]
        self._counter_map[pattern_key] = idx + 1
        return chosen

    def heal(self, text, max_cycles=3):
        """
        执行定向自愈流水线 (多变体轮转)
        """
        current_text = text
        changes_log = []

        for cycle in range(max_cycles):
            report = lint_text(current_text, self.profile)
            if report["passed"] and report["score"] >= 95:
                break

            # 1. 动态轮换代换抽象情绪
            for pool in self.DYNAMIC_EMOTION_POOLS:
                pat = pool["pattern"]
                matches = list(re.finditer(pat, current_text))
                if matches:
                    # 从后往前替换避免偏移
                    for m in reversed(matches):
                        replacement = self._get_next_variant(pat, pool["variants"])
                        start, end = m.span()
                        current_text = current_text[:start] + replacement + current_text[end:]
                        changes_log.append(f"【自愈: 生理物理化 ({pool['category']})】将 '{m.group(0)}' 替换为 '{replacement}'")

            # 2. 修复陈词滥调比喻
            for pat, replacement in self.CLICHE_METAPHOR_FIXES:
                if re.search(pat, current_text):
                    current_text, count = re.subn(pat, replacement, current_text)
                    if count > 0:
                        changes_log.append(f"【自愈: 剔除烂俗比喻】将 '{pat}' 精炼为 '{replacement}' ({count}处)")

            # 3. 清理公文套话
            for pat, replacement in self.BUREAUCRATIC_FIXES:
                if re.search(pat, current_text):
                    current_text, count = re.subn(pat, replacement, current_text)
                    if count > 0:
                        changes_log.append(f"【自愈: 斩断公文病】清理 '{pat}' ({count}处)")

            # 4. 修复段末人生导师式总结升华
            paragraphs = current_text.split("\n")
            healed_paras = []
            
            for p in paragraphs:
                p_clean = p.strip()
                if not p_clean:
                    healed_paras.append(p)
                    continue
                # 检查段末是否命中鸡汤升华
                is_preachy = False
                preach_patterns = [r"这就是人生.*", r"只要.*就总有.*", r"这不仅是.*更是.*", r"或许.*才[是会].*", r"总有.*的一天", r"或许.*的意义"]
                for pat in preach_patterns:
                    if re.search(pat, p_clean[-60:]):
                        is_preachy = True
                        break
                if is_preachy:
                    sub_sentences = [s for s in re.split(r'([。！？])', p_clean) if s]
                    valid_parts = []
                    for k in range(0, len(sub_sentences), 2):
                        s_text = sub_sentences[k]
                        s_punct = sub_sentences[k+1] if k+1 < len(sub_sentences) else "。"
                        if not any(re.search(pat, s_text) for pat in preach_patterns):
                            valid_parts.append(s_text + s_punct)
                    cut_ending = self.HARD_CUT_ENDINGS[(cycle + len(healed_paras)) % len(self.HARD_CUT_ENDINGS)]
                    valid_parts.append(cut_ending)
                    fixed_p = "".join(valid_parts)
                    changes_log.append(f"【自愈: 物理硬切断章】砍断段末人生说教，替换为: '{cut_ending}'")
                    healed_paras.append(fixed_p)
                else:
                    healed_paras.append(p)

            current_text = "\n".join(healed_paras)

        final_report = lint_text(current_text, self.profile)
        return {
            "healed_text": current_text,
            "original_score": lint_text(text, self.profile)["score"],
            "final_score": final_report["score"],
            "passed": final_report["passed"],
            "changes_log": changes_log,
            "final_report": final_report
        }

    def generate_contextual_heal_prompts(self, text, window_chars=50):
        """
        面向 AI Agent (Claude Code / DSH / Codex) 生成局域语境手术级重写提示词
        提取违规句及其前后上下文窗口，交由大语言模型执行自然重写，杜绝任何机械代换痕迹。
        """
        report = lint_text(text, self.profile)
        tasks = []

        for pool in self.DYNAMIC_EMOTION_POOLS:
            pat = pool["pattern"]
            for m in re.finditer(pat, text):
                start, end = m.span()
                ctx_start = max(0, start - window_chars)
                ctx_end = min(len(text), end + window_chars)
                snippet = text[ctx_start:ctx_end]
                tasks.append({
                    "type": "emotion_abstract_trap",
                    "offending_term": m.group(0),
                    "context_snippet": f"...{snippet}...",
                    "instruction": f"请针对上下文将抽象情绪词【{m.group(0)}】重写为贴合该角色当下处境的微观物理动作、生理反射或器物交互，严禁使用任何机械成语或烂俗套路。"
                })

        return {
            "total_violations": len(tasks),
            "original_score": report["score"],
            "rewrite_tasks": tasks
        }

if __name__ == "__main__":
    healer = AutoHealer()
    dirty_text = """李火旺心中一紧，感到一阵钻心的痛，像生锈的铁冰锥刺入骨头。
接着他又感到一阵钻心的痛，心中一紧。
或许，这就是残酷的人生吧，只要活着就总有一天能看到希望。"""

    print("原始文本:\n", dirty_text)
    res = healer.heal(dirty_text)
    print("\n" + "=" * 50)
    print(f"自愈后得分: {res['original_score']} -> {res['final_score']} 分 | 达标: {res['passed']}")
    print("修复修改日志 (注意观察多处重复词是否采用了不同的物理反应):")
    for log in res["changes_log"]:
        print("  *", log)
    print("\n自愈后纯净正文:\n", res["healed_text"])
