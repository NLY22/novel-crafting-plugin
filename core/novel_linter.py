# -*- coding: utf-8 -*-
"""
通用小说微观代码级 Linter 静态质检规则库 (Universal Fiction Linter) - Plugin Core Module
根据通用小说工程化工具设计指南，严格落实 5 大通用红线与题材专属禁忌门禁。
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

# 通用小说去 AI 味核心质检规则矩阵 (Universal Fiction Linter Rules)
UNIVERSAL_LINTER_RULES = {
    # 1. 抽象情绪滥调拦截器 (Emotion Abstract Trap)
    "abstract_emotion_patterns": [
        (r"(?:钻心的痛|钻心之痛|痛彻心扉|痛[，,]\s*钻心[的的]痛|痛，太痛了)", "情绪悬浮，必须替换为神经反射、冷汗、肢体抽搐等冰冷生理反应"),
        (r"(?:心中(?:一紧|一震|大骇|泛起|升起|掀起|充满了)|心头(?:猛然一紧|一颤)|咯噔一下)", "泛滥心跳滥调，必须替换为视线凝固、呼吸阻滞、停下动作等外在事实"),
        (r"(?:倒吸(?:一[口把]|凉气)|瞳孔(?:骤缩|剧烈收缩)|骇然(?:失色)?|不可思议地瞪大)", "网文机械模板词，严禁使用"),
        (r"(?:嘴角勾起|冷笑连连|杀意凛然|眼前一阵发黑)", "程式化面部/心理标签词，缺乏微观真实度")
    ],

    # 2. 人生导师式鸡汤升华拦截器 (Life-Coach Preach Trap)
    "philosophical_ending_patterns": [
        (r"(?:这就是人生.*|只要.*就总有.*|但只要.*总有.*|不仅是.*更是.*|或许.*才[是会].*|总有.*的一天|期待.*更多可能)", 
         "严禁段末/章末说教升华。章节结尾必须硬切在物理动作、悬念对白或具体道具器物上")
    ],

    # 3. 悬浮无增量修辞拦截器 (Metaphor Density & Scale)
    "metaphor_constraints": {
        "max_density_per_kilo_words": 2.5,  # 每千字比喻数 <= 2.5 个
        "forbidden_cliche_metaphors": [
            (r"像一?[把座只群个]?生锈的?.*冰锥", "生锈冰锥滥俗机械比喻"),
            (r"如大山一般|像大山一样", "大山机械比喻"),
            (r"像断了线的风筝", "断线风筝套路比喻"),
            (r"如同决堤的洪水", "决堤洪水套路比喻")
        ]
    },

    # 4. 镜头锚定度检测 (Scenery Water Ratio)
    "max_scenery_sentence_ratio": 0.15,  # 严格控制在 15% 以下，镜头必须死死锁定人物动态交互

    # 5. 语言节奏突发度 (Sentence Burstiness)
    "min_burstiness_score": 0.60  # 突发度必须 >= 0.60，多用短句、单字行与打断式对白
}

PURE_SCENE_PATTERNS = [
    r"(?:夜色|天色|残阳|月光|晨曦|乌云|晚霞|日光|夕阳)",
    r"(?:冷风|狂风|夜风|微风|寒风|秋风|清风)(?:呼啸|掠过|吹|刮|拂过)",
    r"(?:小雨|暴雨|大雨|雨水|细雨)(?:淅淅沥沥|倾盆|拍打|砸|笼罩)",
    r"(?:溶洞|四周|空气|大堂|房间|走廊|街道|院落)(?:一片昏暗|昏暗无光|死一般寂静|弥漫着|静悄悄)",
    r"(?:枯树|杂草|苔藓|破庙|街灯|落叶)(?:在风中|丛生|斑驳|闪烁)"
]

BUREAUCRATIC_PATTERNS = [
    r"进行[了的]?(?:调整|测试|思考|观察|包扎|清理|攻击)",
    r"随着.*的(?:发展|推移|到来)",
    r"不可否认",
    r"毫无疑问",
    r"无形中"
]

def load_profile(profile_name_or_path=None):
    """动态加载独立文风档案"""
    if profile_name_or_path and os.path.exists(profile_name_or_path):
        with open(profile_name_or_path, "r", encoding="utf-8") as f:
            return json.load(f)

    if profile_name_or_path:
        candidate = os.path.join(DEFAULT_PROFILE_DIR, f"{profile_name_or_path}.json")
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                return json.load(f)

    if os.path.exists(DEFAULT_PROFILE_DIR):
        for f in os.listdir(DEFAULT_PROFILE_DIR):
            if f.endswith(".json"):
                with open(os.path.join(DEFAULT_PROFILE_DIR, f), "r", encoding="utf-8") as fp:
                    return json.load(fp)

    return None

def lint_text(text, profile=None):
    """
    运行全题材通用 Linter 静态代码级体检
    """
    clean_text = text.strip()
    total_chars = len(clean_text)
    if total_chars == 0:
        return {"passed": False, "score": 0, "violations": ["文本为空"], "warnings": [], "metrics": {}}

    report = {
        "passed": True,
        "score": 100,
        "violations": [],
        "warnings": [],
        "metrics": {}
    }

    # 1. 抽象情绪滥调审查 (Emotion Abstract Trap)
    for pattern, reason in UNIVERSAL_LINTER_RULES["abstract_emotion_patterns"]:
        matches = re.findall(pattern, clean_text)
        if matches:
            report["passed"] = False
            report["score"] -= 15 * len(matches)
            report["violations"].append(f"【抽象情绪滥调】发现 {len(matches)} 处 '{matches[0]}': {reason}")

    # 2. 人生导师式鸡汤升华拦截 (Life-Coach Preach Trap)
    sentences = [s.strip() for s in re.split(r'[。！？\n]', clean_text) if s.strip()]
    if sentences:
        tail_sentences = sentences[-3:]
        for ts in tail_sentences:
            for pattern, reason in UNIVERSAL_LINTER_RULES["philosophical_ending_patterns"]:
                if re.search(pattern, ts):
                    report["passed"] = False
                    report["score"] -= 25
                    report["violations"].append(f"【结尾升华恶习】末尾出现哲学说教总结: '{ts}' ({reason})")

    # 3. 公文病句式检查
    for pattern in BUREAUCRATIC_PATTERNS:
        matches = re.findall(pattern, clean_text)
        if matches:
            report["passed"] = False
            report["score"] -= 10 * len(matches)
            report["violations"].append(f"【公文病句式】发现套话/冗余句式: '{matches[0]}'")

    # 4. 悬浮无增量修辞拦截器 (Metaphor Density & Scale)
    metaphor_pattern = re.compile(r'(?:像|宛如|仿佛|如同|犹如|好似)')
    metaphors = metaphor_pattern.findall(clean_text)
    metaphor_count = len(metaphors)
    metaphor_density = (metaphor_count / total_chars) * 1000 if total_chars else 0
    report["metrics"]["比喻数"] = metaphor_count
    report["metrics"]["比喻密度(个/千字)"] = round(metaphor_density, 2)
    
    max_density = UNIVERSAL_LINTER_RULES["metaphor_constraints"]["max_density_per_kilo_words"]
    if metaphor_density > max_density and total_chars >= 400:
        report["passed"] = False
        report["score"] -= 15
        report["violations"].append(f"【比喻密度超标】当前每千字 {metaphor_density:.2f} 个比喻 (红线上限为 {max_density} 个)")

    for pat, desc in UNIVERSAL_LINTER_RULES["metaphor_constraints"]["forbidden_cliche_metaphors"]:
        cliche_matches = re.findall(pat, clean_text)
        if cliche_matches:
            report["passed"] = False
            report["score"] -= 15 * len(cliche_matches)
            report["violations"].append(f"【陈词滥调比喻】命中滥俗比喻: '{cliche_matches[0]}' ({desc})")

    # 5. 镜头锚定度检测 (Scenery Water Ratio)
    scene_sentences = [
        s for s in sentences 
        if not (('“' in s and '”' in s) or ('"' in s) or ('「' in s)) and any(re.search(pat, s) for pat in PURE_SCENE_PATTERNS)
    ]
    scene_ratio = len(scene_sentences) / len(sentences) if sentences else 0
    report["metrics"]["景物注水占比"] = f"{scene_ratio * 100:.1f}%"
    report["metrics"]["总字数"] = total_chars
    report["metrics"]["总句数"] = len(sentences)

    max_scene_ratio = UNIVERSAL_LINTER_RULES["max_scenery_sentence_ratio"]
    if scene_ratio > max_scene_ratio:
        report["passed"] = False
        report["score"] -= 15
        report["violations"].append(f"【景物描写注水超标】占比高达 {scene_ratio * 100:.1f}% (红线上限为 {max_scene_ratio * 100:.1f}%)")

    # 6. 语言节奏突发度 (Sentence Burstiness)
    if len(sentences) >= 4:
        s_lens = [len(s) for s in sentences]
        avg_l = sum(s_lens) / len(s_lens)
        var = sum((x - avg_l) ** 2 for x in s_lens) / len(s_lens)
        burstiness = (var ** 0.5) / avg_l if avg_l else 0
        report["metrics"]["突发度(Burstiness)"] = f"{burstiness:.2f}"
        min_burst = UNIVERSAL_LINTER_RULES["min_burstiness_score"]
        if burstiness < min_burst:
            report["warnings"].append(f"【句式略微平缓】突发度 {burstiness:.2f} (红线要求 >= {min_burst}，建议强化短句断音)")
            report["score"] -= 5

    # 7. 专属文风禁忌词静态扫描 (Style-Specific Taboos)
    prof_name = profile.get("corpus_name", "") if profile else ""
    if "顾漫" in prof_name or "微微" in prof_name:
        gu_man_taboos = [
            (r"(?:某机关|机关单位|机关大院|综合办公室|立式空调|复印机碳粉|红头材料|分管主任|自查要点)", "老干部体制内公文叙事，严重破坏顾漫式灵动青春网游神韵"),
            (r"(?:部委正科|如数家珍地报菜名|福利房|父母老高工|门当户对)", "中年催婚相亲报菜名，违背网瘾少女机敏与轻快恋爱感")
        ]
        for pat, reason in gu_man_taboos:
            m = re.findall(pat, clean_text)
            if m:
                report["passed"] = False
                report["score"] -= 15 * len(m)
                report["violations"].append(f"【顾漫文风违规】命中破坏性禁忌 '{m[0]}': {reason}")

    elif "狐尾" in prof_name or "道诡" in prof_name:
        fox_tail_taboos = [
            (r"(?:龙王归来|蝼蚁.*狂妄|不自量力|废柴.*退婚|桀骜不驯地冷笑)", "传统套路玄幻装逼台词，破坏狐尾克系惊悚神韵"),
            (r"(?:阳光总在风雨后|心中充满了正能量|只要心怀希望)", "圣母鸡汤感叹，违背真假撕裂与精神失调的冷硬现实")
        ]
        for pat, reason in fox_tail_taboos:
            m = re.findall(pat, clean_text)
            if m:
                report["passed"] = False
                report["score"] -= 15 * len(m)
                report["violations"].append(f"【道诡文风违规】命中破坏性禁忌 '{m[0]}': {reason}")

    # 8. 检查商业长篇单章刚性篇幅容量 (2,800 ~ 4,000 字)
    is_full_chapter = ("第" in clean_text[:80] and "章" in clean_text[:80]) or total_chars >= 800
    if is_full_chapter:
        if total_chars < 2200:
            report["passed"] = False
            report["score"] -= 20
            report["violations"].append(
                f"【单章篇幅严重不足】当前仅 {total_chars} 字！商业小说标准单章黄金区间为 2,800 ~ 4,000 字。"
                "篇幅过短会导致情节仓促快进、缺乏博弈拉扯。必须依据四场次预算展开！"
            )
        elif total_chars < 2800:
            report["warnings"].append(
                f"【单章篇幅略微紧凑】当前字数 {total_chars} 字（标准大章建议达到 2,800 ~ 3,500 字，以确保充分沉浸感）。"
            )

    report["score"] = max(0, report["score"])
    return report

class NovelLinter:
    def __init__(self, profile=None):
        self.profile = profile or load_profile()

    def lint(self, text):
        return lint_text(text, self.profile)

    def evaluate(self, text):
        rep = self.lint(text)
        return rep["score"], rep["violations"]

    def print_report(self, text, label="待测文本"):
        rep = lint_text(text, self.profile)
        print(f"\n==========================================")
        print(f" 🛡️  Universal Fiction Linter 质检报告: {label}")
        print(f"==========================================")
        print(f"综合评分: {rep['score']} 分 | 达标状态: {'✅ 通过' if rep['passed'] else '❌ 拦截'}")
        print(f"度量指标: {json.dumps(rep['metrics'], ensure_ascii=False)}")
        if rep['violations']:
            print(f"🛑 违规拦截项 ({len(rep['violations'])} 处):")
            for v in rep['violations']:
                print(f"  - {v}")
        if rep['warnings']:
            print(f"⚠️ 优化警示 ({len(rep['warnings'])} 处):")
            for w in rep['warnings']:
                print(f"  - {w}")
        print(f"==========================================\n")
        return rep

if __name__ == "__main__":
    l = NovelLinter()
    test_text = "李火旺心中一紧，感到一阵钻心的痛，像生锈的铁冰锥刺入骨头。他看着窗外的晚霞，心想这就是人生啊。"
    l.print_report(test_text, "违规样本测试")
