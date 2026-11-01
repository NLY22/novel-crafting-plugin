# -*- coding: utf-8 -*-
"""
Novel-Crafting Universal MCP Server (Model Context Protocol)
纯 Python 标准库原生实现，零第三方重型依赖 (无需 pip install mcp)，
为 Claude Code (cc), DeepSeek Harness (dsh), Codex, Cursor, Antigravity 提供跨平台原生工具调用能力。
"""

import sys
import io
import os
import json

# 确保 UTF-8 编码
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 导入核心模块
_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = _CURR_DIR
_CORE_DIR = os.path.join(_CURR_DIR, "core")
if _CORE_DIR not in sys.path:
    sys.path.insert(0, _CORE_DIR)

from narrative_engine import NarrativeEngine
from style_compiler import StyleCompiler
from prompt_builder import build_style_prompt
from novel_linter import NovelLinter, load_profile
from auto_healer import AutoHealer
from longitudinal_linter import LongitudinalLinter
from world_state_ledger import WorldStateLedger
from macro_tension_analyzer import MacroTensionAnalyzer
from branching_generator import generate_branches
from plot_tracker import PlotTracker
from state_diff_extractor import StateDiffExtractor
from scene_expander import SceneExpander
from novel_learner import MasterpieceLearner

SERVER_INFO = {
    "name": "novel-crafting",
    "version": "3.2.0"
}

TOOLS = [
    {
        "name": "novel_pass1_beat_sheet",
        "description": "【Pass 1 剧力推进层】规划单章四场次分镜事件骨架，并执行大事件、戏剧阻力、信息差与硬切断章的断言校验 (Assert)。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_num": {"type": "integer", "description": "章节序号，如 5"},
                "chapter_title": {"type": "string", "description": "章节标题，如 '料房药渣'"},
                "core_event": {"type": "string", "description": "本章改变人物处境或心理状态的核心大事件"},
                "dramatic_resistance": {"type": "string", "description": "外部施压变量或行动阻力"},
                "information_gap": {"type": "string", "description": "在场人物之间的认知反差与潜台词"},
                "spatio_temporal": {"type": "string", "description": "时间与主场景空间，如 '深夜 / 地下料房'"},
                "cut_point": {"type": "string", "description": "收尾定格硬切点 (严禁哲学感叹，定格在动作或器物上)"}
            },
            "required": ["chapter_num", "chapter_title", "core_event", "dramatic_resistance", "information_gap", "spatio_temporal", "cut_point"]
        }
    },
    {
        "name": "novel_compile_style_prompt",
        "description": "【Pass 2 文风渲染层】基于指定名家文风 (如'顾漫'/'狐尾的笔'/'卖报小郎君') 编译注入原著 Few-Shot 样本切片、专属手艺法则与 3000 字四场次配额的提示词。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_name": {"type": "string", "description": "作家名称或作品名，如 '顾漫' 或 '道诡异仙'"},
                "scene_desc": {"type": "string", "description": "本场戏的核心剧情任务描述"},
                "target_words": {"type": "integer", "description": "篇幅目标，默认 3000 字", "default": 3000}
            },
            "required": ["profile_name", "scene_desc"]
        }
    },
    {
        "name": "novel_lint_text",
        "description": "【Micro Universal Linter】对小说正文草稿进行代码级静态审查，检测抽象情绪滥调 (钻心的痛/心中一紧)、结尾人生导师升华、无增量比喻密度、景物注水率及长短句突发度。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待审查的小说正文草稿"},
                "profile_name": {"type": "string", "description": "挂载的文风画像名称 (可选)"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "novel_auto_heal",
        "description": "【Auto-Healer 文本自愈器】将审查未通过的草稿进行定向物理化重写，将抽象情绪替换为生理事实，将鸡汤说教结尾硬切断章，自愈跑满 100 分。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "有瑕疵的小说正文草稿"},
                "profile_name": {"type": "string", "description": "挂载的文风画像名称 (可选)"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "novel_longitudinal_audit",
        "description": "【反土拨鼠之日纵向审查】计算章节起手式与收口式的向量余弦相似度，检查是否连续出现看窗外喝茶叹气或清晨醒来套路，并校验时空拓扑连续度。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_num": {"type": "integer", "description": "当前章节号"},
                "title": {"type": "string", "description": "章节标题"},
                "text": {"type": "string", "description": "正文内容"},
                "space": {"type": "string", "description": "发生场景", "default": "公共场景"},
                "time_str": {"type": "string", "description": "发生时间", "default": "白天"}
            },
            "required": ["chapter_num", "title", "text"]
        }
    },
    {
        "name": "novel_world_state_brief",
        "description": "【World State Ledger】获取世界线长程因果状态账本简报，排查主角生理伤势愈合倒计时、随身银两物资及 NPC 疑心仇恨矩阵 (彻底杜绝吃书)。",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "novel_macro_tension",
        "description": "【整卷张力心电图逆向】分析指定文本或章节的戏剧冲突张力值 (10-100)，判定其呼吸状态 (爆发/暗流/蓄势)。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待分析的章节文本或小说切片"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "novel_branching",
        "description": "【剧情十字路口分支推演】当面临重大抉择或卡文时，自动推演 A (强冲突)、B (心理暗流利益博弈)、C (认知颠覆与荒诞转折) 三种高张力走向供创作者拍板。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scene_context": {"type": "string", "description": "当前现场情境描述"},
                "current_objective": {"type": "string", "description": "当前核心诉求或困境"}
            },
            "required": ["scene_context", "current_objective"]
        }
    },
    {
        "name": "novel_due_reminders",
        "description": "【伏笔时间锁追踪】查询指定章节到期必须回收或引爆的暗线提示。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_num": {"type": "integer", "description": "当前准备撰写的章节号"}
            },
            "required": ["chapter_num"]
        }
    },
    {
        "name": "novel_extract_state_diff",
        "description": "【正文因果差量提取与状态机同步】分析已写就的章节正文，自动反向提取伤势、银钱开支、道具增减与时间流逝，可自动更新合并至 World State Ledger。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_num": {"type": "integer", "description": "当前章节号"},
                "text": {"type": "string", "description": "本章正文内容"},
                "apply_to_ledger": {"type": "boolean", "description": "是否直接合并更新至状态机账本", "default": True}
            },
            "required": ["chapter_num", "text"]
        }
    },
    {
        "name": "novel_progressive_turn_prompt",
        "description": "【四场次多轮渐进式生成调度】为特定场次 (Scene 1-4) 编译专项扩写指令，强制锁定该场次字数与描写焦点，彻底根除 1200 字仓促大纲快进病。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scene_id": {"type": "integer", "description": "场次编号 (1-4)"},
                "scene_plan_detail": {"type": "string", "description": "本场细分动作规划"},
                "prev_scene_tail": {"type": "string", "description": "上一场次结尾的最后两句话 (用于咬合接缝)", "default": ""},
                "author_style": {"type": "string", "description": "名家文风风格描述", "default": "名家风格"}
            },
            "required": ["scene_id", "scene_plan_detail"]
        }
    },
    {
        "name": "novel_contextual_heal_prompts",
        "description": "【局域语境手术级重写提示词】提取草稿中违规词的前后上下文窗口，为 AI Agent 生成上下文无缝重写提示，杜绝任何机械代换痕迹。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "草稿正文"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "novel_learn_masterpiece",
        "description": "【全息小说逆向工程研习器】对任意小说语料进行七维全息逆向工程研习（全息解析其所有内容、写法、思路、框架、情节、文风、文字编排），输出机器级 DNA 蓝图 (.dna.json) 与人类/AI 全息研习参考手册 (.md)。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "corpus_path": {"type": "string", "description": "小说全本或样本 txt 文件绝对路径"},
                "chapters": {"type": "integer", "description": "精读并深度拆解的样本章节数，默认 40 章", "default": 40},
                "output_dir": {"type": "string", "description": "成果保存目录 (默认为 profiles/ 目录)"}
            },
            "required": ["corpus_path"]
        }
    },
    {
        "name": "novel_inspect_masterpiece_dna",
        "description": "【名作 DNA 蓝图检索器】查询已研习小说的特定维度基准：文字编排呼吸律、文风、写法、心智思路、框架节拍、情节因果或世界观门禁。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "novel_name": {"type": "string", "description": "小说名称 (如 '大奉打更人_卖报小郎君', '道诡异仙_狐尾的笔', '微微一笑很倾城（出书版）_顾漫')"},
                "dimension": {
                    "type": "string",
                    "description": "查询维度",
                    "enum": ["all", "typography_pacing", "style_language", "narrative_craft", "author_mindset", "framework_beats", "plot_causality", "world_conception"],
                    "default": "all"
                }
            },
            "required": ["novel_name"]
        }
    }
]

# 单例缓存
_narrative_engine = NarrativeEngine()
_linter = NovelLinter()
_healer = AutoHealer()
_longitudinal_linter = LongitudinalLinter()
_world_ledger = WorldStateLedger()
_macro_analyzer = MacroTensionAnalyzer()
_plot_tracker = PlotTracker()
_diff_extractor = StateDiffExtractor(_world_ledger)
_scene_expander = SceneExpander()

def handle_tool_call(tool_name, args):
    try:
        if tool_name == "novel_pass1_beat_sheet":
            card = {
                "core_event": args.get("core_event"),
                "dramatic_resistance": args.get("dramatic_resistance"),
                "information_gap": args.get("information_gap"),
                "spatio_temporal": args.get("spatio_temporal"),
                "cut_point": args.get("cut_point"),
                "scenes": args.get("scenes", {})
            }
            sheet = _narrative_engine.generate_beat_sheet(args.get("chapter_num"), args.get("chapter_title"), card)
            res = sheet["markdown"]
            if not sheet["passed"]:
                res = f"❌ 【断言失败违规项】:\n" + "\n".join(f"- {v}" for v in sheet["violations"]) + "\n\n" + res
            return res

        elif tool_name == "novel_compile_style_prompt":
            return build_style_prompt(args.get("profile_name"), args.get("scene_desc"), args.get("target_words", 3000))

        elif tool_name == "novel_lint_text":
            prof = load_profile(args.get("profile_name")) if args.get("profile_name") else None
            linter = NovelLinter(prof) if prof else _linter
            rep = linter.lint(args.get("text"))
            return json.dumps(rep, ensure_ascii=False, indent=2)

        elif tool_name == "novel_auto_heal":
            prof = load_profile(args.get("profile_name")) if args.get("profile_name") else None
            healer = AutoHealer(prof) if prof else _healer
            res = healer.heal(args.get("text"))
            return json.dumps(res, ensure_ascii=False, indent=2)

        elif tool_name == "novel_longitudinal_audit":
            audit = _longitudinal_linter.audit_chapter(
                args.get("chapter_num"),
                args.get("text"),
                args.get("space", "公共场景"),
                args.get("time_str", "白天")
            )
            return json.dumps(audit, ensure_ascii=False, indent=2)

        elif tool_name == "novel_world_state_brief":
            return _world_ledger.generate_ledger_brief()

        elif tool_name == "novel_macro_tension":
            score = _macro_analyzer.analyze_chapter_tension(args.get("text"))
            if score >= 65:
                state = "🔥 冲突爆发 / 决断交锋"
            elif score >= 45:
                state = "⚡ 暗流交织 / 危机逼近"
            else:
                state = "🍃 蓄势松弛 / 生活沉淀"
            return f"张力得分: {score}/100\n当前生命呼吸节律: {state}"

        elif tool_name == "novel_branching":
            branches = generate_branches(args.get("scene_context"), args.get("current_objective"))
            return json.dumps(branches, ensure_ascii=False, indent=2)

        elif tool_name == "novel_due_reminders":
            reminders = _plot_tracker.get_due_reminders(args.get("chapter_num"))
            return json.dumps(reminders, ensure_ascii=False, indent=2)

        elif tool_name == "novel_extract_state_diff":
            diff = _diff_extractor.extract_diff_from_chapter(args.get("chapter_num"), args.get("text"))
            if args.get("apply_to_ledger", True):
                brief = _diff_extractor.apply_diff_to_ledger(diff)
                diff["updated_ledger_brief"] = brief
            return json.dumps(diff, ensure_ascii=False, indent=2)

        elif tool_name == "novel_progressive_turn_prompt":
            return _scene_expander.get_turn_prompt(
                args.get("scene_id"),
                args.get("scene_plan_detail"),
                args.get("prev_scene_tail", ""),
                args.get("author_style", "名家风格")
            )

        elif tool_name == "novel_contextual_heal_prompts":
            prompts = _healer.generate_contextual_heal_prompts(args.get("text"))
            return json.dumps(prompts, ensure_ascii=False, indent=2)

        elif tool_name == "novel_learn_masterpiece":
            corpus_path = args.get("corpus_path")
            chapters = args.get("chapters", 40)
            output_dir = args.get("output_dir")
            learner = MasterpieceLearner(corpus_path)
            learner.load_corpus()
            dna, md_path = learner.execute_deep_learning(sample_chapters_count=chapters, output_dir=output_dir)
            n_name = dna['novel_name']
            save_dir = output_dir or os.path.dirname(md_path)
            json_target = os.path.join(save_dir, f"{n_name}.dna.json")
            return (
                f"🎉 成功完成对《{n_name}》的七维全息逆向工程研习！\n"
                f"📊 样本覆盖: 前 {dna['sample_chapters_analyzed']} 章 (共 {dna['sample_char_count']:,} 字)\n"
                f"📑 全息研习参考手册已生成: {md_path}\n"
                f"💾 机器级 DNA 蓝图已保存: {json_target}\n\n"
                f"【核心数理指纹速览】:\n"
                f"- 段落呼吸: 平均 {dna['dimension_1_typography_pacing']['avg_paragraph_length']} 字/段 | 单句独段率 {dna['dimension_1_typography_pacing']['single_sentence_paragraph_ratio']:.1%}\n"
                f"- 动作伴随对白比: {dna['dimension_1_typography_pacing']['dialogue_action_weaving']['action_tagged_dialogue_ratio']:.1%}\n"
                f"- 句式突发度: {dna['dimension_2_style_language']['sentence_burstiness']} ({dna['dimension_2_style_language']['sentence_cadence']['style_category']})\n"
                f"- 主导感官: {dna['dimension_2_style_language']['dominant_sense']}\n"
                f"- 镜头焦点: {dna['dimension_3_narrative_craft']['camera_primary_focus']}\n"
                f"- 断章规范: 动作硬切 {dna['dimension_5_framework_beats']['cliffhanger_hook_distribution']['action_cut']:.1%} | 对白硬切 {dna['dimension_5_framework_beats']['cliffhanger_hook_distribution']['dialogue_cut']:.1%}"
            )

        elif tool_name == "novel_inspect_masterpiece_dna":
            novel_name = args.get("novel_name")
            dimension = args.get("dimension", "all")
            prof_dir = os.path.join(PLUGIN_ROOT, "profiles")
            dna_file = os.path.join(prof_dir, f"{novel_name}.dna.json")
            if not os.path.exists(dna_file):
                # 尝试模糊匹配
                matches = [f for f in os.listdir(prof_dir) if novel_name in f and f.endswith(".dna.json")]
                if matches:
                    dna_file = os.path.join(prof_dir, matches[0])
                else:
                    return f"❌ 未找到《{novel_name}》的 DNA 蓝图，请先调用 novel_learn_masterpiece 进行逆向研习！"
            
            with open(dna_file, "r", encoding="utf-8") as f:
                dna_data = json.load(f)

            dim_key_map = {
                "typography_pacing": "dimension_1_typography_pacing",
                "style_language": "dimension_2_style_language",
                "narrative_craft": "dimension_3_narrative_craft",
                "author_mindset": "dimension_4_author_mindset",
                "framework_beats": "dimension_5_framework_beats",
                "plot_causality": "dimension_6_plot_causality",
                "world_conception": "dimension_7_world_conception"
            }
            if dimension != "all" and dimension in dim_key_map:
                res = {
                    "novel_name": dna_data.get("novel_name"),
                    "dimension": dimension,
                    "metrics": dna_data.get(dim_key_map[dimension])
                }
                return json.dumps(res, ensure_ascii=False, indent=2)
            return json.dumps(dna_data, ensure_ascii=False, indent=2)

        else:
            return f"未知工具: {tool_name}"
    except Exception as e:
        return f"执行工具 '{tool_name}' 异常: {str(e)}"

def send_response(response_dict):
    body = json.dumps(response_dict, ensure_ascii=False)
    sys.stdout.write(body + "\n")
    sys.stdout.flush()

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        # 处理可能的前缀头 (Content-Length 等)
        if line.startswith("Content-Length:"):
            # 兼容 HTTP 格式帧
            length = int(line.split(":")[1].strip())
            # 跳过空行
            sys.stdin.readline()
            payload = sys.stdin.read(length)
            req = json.loads(payload)
        else:
            req = json.loads(line)

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": SERVER_INFO
                }
            })
        elif method == "notifications/initialized":
            # 协议要求通知无需回包
            pass
        elif method == "ping":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })
        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS
                }
            })
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            out_text = handle_tool_call(tool_name, args)
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(out_text)
                        }
                    ]
                }
            })
        else:
            if req_id is not None:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })

if __name__ == "__main__":
    main()
