# -*- coding: utf-8 -*-
"""
Grill-Me 深度对齐与设定质询引擎 (Grill-Me Inquisition Engine)
专为虚构小说打造的高严苛度“总编级”对齐工具。
杜绝 AI 自主性抢跑，强制在动笔前与创作者深度对齐世界观代价、人物缺陷与主线矛盾。
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

class GrillEngine:
    """小说创作深度质询与设定对齐引擎"""

    DIMENSIONS = [
        {
            "id": "hook_and_genre",
            "name": "1. 核心脑洞与题材定位 (Hook & Genre)",
            "question": "你的核心脑洞到底是什么？如果只用一句话向读者推销，最吸引人的‘反差’或‘奇观’在哪里？",
            "challenge": "【质询追问】：该题材当下市场套路严重，你对标的名家文风是哪一本（如大奉探案、道诡克系、顾漫甜宠）？你的核心差异化卖点是什么？读者获得的核心情绪价值（爽/虐/惊悚/治愈）是什么？",
            "keywords_required": ["题材", "对标", "反差", "看点"]
        },
        {
            "id": "world_and_cost",
            "name": "2. 世界观与代价法则工程 (The Law of Cost)",
            "question": "你的核心力量体系（超能力/修真/金手指/黑科技）遵循什么冷酷的底层法则？",
            "challenge": "【严苛拷问】：凡有力量必有不可逆代价！施法会灼烧内脏、扣除寿命、还是导致精神异化？如果主角能无成本无限使用，战力在第20章必崩！你的‘代价机制’具体是什么？",
            "keywords_required": ["代价", "异化", "限制", "负面效果"]
        },
        {
            "id": "class_and_hegemony",
            "name": "3. 社会阶级断层与暴力机器 (Class & Hegemony)",
            "question": "这个世界的生存资源与特权被谁垄断？底层百姓靠什么活着？",
            "challenge": "【现实拷问】：维持统治的暴力机器是什么（官僚/宗门/财阀/密探）？底层人若触犯红线会遭遇什么？主角在阶级结构中处于哪一层？他的‘阶级认知盲区’在哪里？",
            "keywords_required": ["阶级", "垄断", "底层", "秩序"]
        },
        {
            "id": "character_and_reflex",
            "name": "4. 人物心智缺陷与生理应激 (Flaw & Stress Reflex)",
            "question": "主角绝不能是全能圣母或脸谱冷酷。他最大的心智缺陷是什么？他最隐秘的恐惧是什么？",
            "challenge": "【深度剖析】：面对极端恐惧、剧痛或至亲危机时，他本能的‘生理微动作’是什么？（严禁回答‘心中一紧/倒吸凉气’，必须转化为咬破腮肉、指节发白、摩挲刀柄铜片等具体动作）。",
            "keywords_required": ["缺陷", "恐惧", "动作", "应激"]
        },
        {
            "id": "plot_and_clock",
            "name": "5. 主线倒计时钟与第一卷高潮 (Ticking Clock & Climax)",
            "question": "推动主角入局的‘倒计时钟 (Ticking Clock)’是什么？他不采取行动的最惨结局是什么？",
            "challenge": "【结构拷问】：第一卷计划多少章？中间点（Midpoint）的重大反转是什么？卷末大决战主角即便赢了，必须付出什么‘不可逆的代价’？",
            "keywords_required": ["倒计时", "危机", "中点", "结局"]
        },
        {
            "id": "foreshadowing_traps",
            "name": "6. 伏笔时间锁与反转证据 (Foreshadowing & Traps)",
            "question": "第一卷最关键的伪装与真相是什么？你打算在第几章埋下第一个看似不起眼的物证？",
            "challenge": "【防吃书质询】：读者看到最终真相揭晓时，能不能在第几章回头找到铁证？哪个道具或哪句话承担了‘假线索（佯谬）’功能？",
            "keywords_required": ["真相", "道具", "埋设", "反转"]
        }
    ]

    def __init__(self, project_dir=None):
        self.project_dir = project_dir

    def get_inquisition_plan(self):
        """获取完整的质询大纲"""
        return self.DIMENSIONS

    def audit_response(self, dim_id, answer_text):
        """对创作者的回答进行深度质量审查"""
        issues = []
        clean_text = answer_text.strip()
        
        if len(clean_text) < 15:
            issues.append("回答过于简短（少于 15 字），缺乏具体的设定颗粒度，容易导致后续情节悬空。")
            
        slop_words = ["心中一紧", "钻心的痛", "骇然", "倒吸凉气", "非常完美", "性格坚毅", "大山", "无敌"]
        found_slop = [w for w in slop_words if w in clean_text]
        if found_slop:
            issues.append(f"检测到抽象情绪/套路词汇: {', '.join(found_slop)}。请将其转化为具体的客观法则或生理动作。")
            
        if dim_id == "world_and_cost" and not any(w in clean_text for w in ["代价", "异化", "反噬", "伤害", "负面", "限制", "痛苦", "损耗"]):
            issues.append("世界观法则缺少明确的【反噬与代价】机制。超自然力量必须绑定不可逆损耗，否则战力必崩。")

        if dim_id == "character_and_reflex" and not any(w in clean_text for w in ["手", "牙", "指", "背", "喉", "肌肉", "汗", "动作", "刀", "眼神"]):
            issues.append("缺少生理应激动作描写。请明确主角在极端压力下下意识的肢体动作。")

        return {
            "passed": len(issues) == 0,
            "issues": issues
        }

    def compile_dossier(self, novel_name, answers, output_file=None):
        """将对齐结果编译为高规格 Markdown 立项备忘录"""
        lines = [
            f"# 🎯 《{novel_name}》设定对齐拷问立项书 (Grill-Me Alignment Dossier)",
            "",
            "> 本立项书由 Grill-Me 质询引擎深度对齐生成，代表创作者已拍板定案的底层契约。",
            "> **AI 协作铁律**：后续所有章节细纲与正文生成，必须 100% 遵守本契约，严禁私自篡改设定！",
            "",
            "---",
            ""
        ]

        for dim in self.DIMENSIONS:
            d_id = dim["id"]
            d_name = dim["name"]
            user_ans = answers.get(d_id, "（未填写）")
            lines.append(f"## {d_name}")
            lines.append(f"**【核心质询题目】**：{dim['question']}")
            lines.append(f"**【总编深度追问】**：{dim['challenge']}")
            lines.append("")
            lines.append(f"### 💡 创作者定案设定：")
            lines.append(f"{user_ans}")
            lines.append("")
            lines.append("---")
            lines.append("")

        lines.append("## ✍️ 授权动笔签字门禁")
        lines.append("- [x] 题材与核心脑洞已对齐")
        lines.append("- [x] 力量不可逆代价已锁死")
        lines.append("- [x] 主角心智缺陷与应激动作已固化")
        lines.append("- [x] 第一卷倒计时危机与伏笔时间锁已排布")
        lines.append("")
        lines.append("> 🟢 **状态：经创作者拍板，本案正式立项！授权进入第一章分镜与撰写阶段。**")

        content = "\n".join(lines)
        if output_file:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 立项书已生成: {output_file}")

        return content

    def run_interactive_cli(self):
        """在控制台以交互方式运行 Grill-Me 质询"""
        print("\n" + "=" * 60)
        print("    🎯  Grill-Me 小说总编级深度对齐拷问器 (Inquisition Console)    ")
        print("=" * 60)
        print("说明：在开始写一本新书前，我们将逐项质询 6 大核心支柱。")
        print("请尽可能具体地回答，拒绝空洞套路词。\n")

        novel_name = input("请输入准备开辟的新书书名 (默认: 未命名新书): ").strip()
        if not novel_name:
            novel_name = "未命名新书"

        answers = {}

        for i, dim in enumerate(self.DIMENSIONS, 1):
            print("\n" + "-" * 60)
            print(f"【维度 {i}/6】{dim['name']}")
            print(f"❓ 问题: {dim['question']}")
            print(f"🔥 拷问: {dim['challenge']}")
            print("-" * 60)

            while True:
                ans = input("\n👉 你的定案想法 (输入完成后按回车): ").strip()
                if not ans:
                    print("⚠️ 回答不能为空，请认真思考后作答。")
                    continue

                audit = self.audit_response(dim["id"], ans)
                if not audit["passed"]:
                    print("\n⚠️ 【总编质询提醒】发现潜在软肋：")
                    for iss in audit["issues"]:
                        print(f"  - {iss}")
                    retry = input("\n是否根据上述意见补充修改？(Y/n，按回车直接继续): ").strip().lower()
                    if retry == "y":
                        continue

                answers[dim["id"]] = ans
                print("✅ 该维度已对齐锁定！")
                break

        print("\n" + "=" * 60)
        print("🎉 恭喜！6 大维度已全部深入对齐！正在生成立项备忘录...")
        
        output_dir = os.path.join(PLUGIN_DIR, "dossiers")
        output_file = os.path.join(output_dir, f"立项对齐书_{novel_name}.md")
        self.compile_dossier(novel_name, answers, output_file)
        print("=" * 60)
        return output_file

if __name__ == "__main__":
    engine = GrillEngine()
    engine.run_interactive_cli()
