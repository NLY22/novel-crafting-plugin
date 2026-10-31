# -*- coding: utf-8 -*-
"""
代码级文本定向自愈修复器 (Novel Auto-Healer & Style Purifier) - Plugin Core Module
通用小说工程化工具核心自愈引擎。
将 Linter 查出的抽象情绪、陈词比喻、人生导师升华等违规坏味道，自动定向重写与物理硬切回填。
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
    """去 AI 味代码级文本自愈修复器"""

    # 抽象情绪物理化代换规则库
    EMOTION_PHYSICAL_MAPPINGS = [
        (r"钻心[的的]痛|痛[，,]\s*钻心[的的]痛|钻心之痛", "后槽牙死死咬破口腔内软肉，血腥味瞬间涌上舌尖"),
        (r"痛彻心扉", "疼得整截脊椎骨剧烈抽搐了一下"),
        (r"心中一紧|心头一紧|心头猛然一紧", "按在袖口里的五指骤然扣紧"),
        (r"心中一震|心中大骇", "后颈的汗毛根根倒竖起来"),
        (r"咯噔一下", "心跳骤然漏了一拍，呼吸猛地一滞"),
        (r"倒吸(?:一[口把]|凉气)", "喉结上下狠狠滚动了一下"),
        (r"瞳孔(?:骤缩|剧烈收缩)", "视线瞬间死死钉在对方的指节上"),
        (r"骇然失色|骇然", "脸色肉眼可见地刷白下来"),
        (r"眼前一阵发黑", "胃里一阵翻江倒海般的酸水狂涌"),
        (r"杀意凛然", "说话的调门陡然压低了半寸"),
        (r"嘴角勾起(?:一抹)?(?:弧度|冷笑)", "嘴角牵起一丝僵硬的弧线")
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

    # 结尾人生导师升华物理硬切备选池
    HARD_CUT_ENDINGS = [
        "门外传来更夫沉闷的铜锣声，一下接着一下，渐行渐远。",
        "他反手插上门闩，铜锁舌咔哒一声咬死，屋里重归死寂。",
        "灶膛里的最后一点火星扑哧暗了下去，空气里只剩下焦糊的松烟气。",
        "他没再回头，伸手将衣领往上拽了拽，快步拐进了逼仄的雨巷。"
    ]

    def __init__(self, profile=None):
        self.profile = profile

    def heal(self, text, max_cycles=3):
        """
        执行定向自愈流水线
        """
        current_text = text
        changes_log = []

        for cycle in range(max_cycles):
            report = lint_text(current_text, self.profile)
            if report["passed"] and report["score"] >= 95:
                break

            # 1. 修复抽象情绪滥调
            for pat, replacement in self.EMOTION_PHYSICAL_MAPPINGS:
                if re.search(pat, current_text):
                    current_text, count = re.subn(pat, replacement, current_text)
                    if count > 0:
                        changes_log.append(f"【自愈: 生理物理化】将 '{pat}' 替换为 '{replacement}' ({count}处)")

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
            sentences = [s.strip() for s in re.split(r'([。！？\n])', current_text) if s.strip()]
            # 重构句子数组
            reconstructed_paras = []
            paragraphs = current_text.split("\n")
            healed_paras = []
            
            for p in paragraphs:
                p_clean = p.strip()
                if not p_clean:
                    healed_paras.append(p)
                    continue
                # 检查段末是否命中鸡汤升华
                is_preachy = False
                preach_patterns = [r"这就是人生.*", r"只要.*就总有.*", r"这不仅是.*更是.*", r"或许.*才[是会].*", r"总有.*的一天"]
                for pat in preach_patterns:
                    if re.search(pat, p_clean[-50:]):
                        is_preachy = True
                        break
                if is_preachy:
                    # 剥离最后的鸡汤句，替换为物理硬切
                    sub_sentences = [s for s in re.split(r'([。！？])', p_clean) if s]
                    valid_parts = []
                    for k in range(0, len(sub_sentences), 2):
                        s_text = sub_sentences[k]
                        s_punct = sub_sentences[k+1] if k+1 < len(sub_sentences) else "。"
                        if not any(re.search(pat, s_text) for pat in preach_patterns):
                            valid_parts.append(s_text + s_punct)
                    if not valid_parts:
                        valid_parts.append(self.HARD_CUT_ENDINGS[0])
                    else:
                        valid_parts.append(self.HARD_CUT_ENDINGS[cycle % len(self.HARD_CUT_ENDINGS)])
                    fixed_p = "".join(valid_parts)
                    changes_log.append("【自愈: 物理硬切断章】砍断段末人生导师总结，替换为具体器物/环境动作定格")
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

if __name__ == "__main__":
    healer = AutoHealer()
    dirty_text = """李火旺心中一紧，感到一阵钻心的痛，像生锈的铁冰锥刺入骨头。
他深吸了一口气，对现场进行了仔细的观察。
或许，这就是残酷的人生吧，只要活着就总有一天能看到希望。"""

    print("原始文本:\n", dirty_text)
    res = healer.heal(dirty_text)
    print("\n" + "=" * 50)
    print(f"自愈后得分: {res['original_score']} -> {res['final_score']} 分 | 达标: {res['passed']}")
    print("修复修改日志:")
    for log in res["changes_log"]:
        print("  *", log)
    print("\n自愈后纯净正文:\n", res["healed_text"])
