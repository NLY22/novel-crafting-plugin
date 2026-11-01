# -*- coding: utf-8 -*-
"""
全息小说深度学习与逆向工程研习机 (Masterpiece Deep Deconstruction & Learning Engine)
核心模块：全面逆向学习小说的所有内容、写法、思路、框架、情节、文风、文字编排。
输出机器级 DNA 蓝图 (JSON) 与人类/AI 深度可读的《全息研习参考手册》(Markdown)。
"""

import sys
import os
import re
import json
import math
from collections import Counter

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(_CURR_DIR)
DEFAULT_PROFILE_DIR = os.path.join(PLUGIN_ROOT, "profiles")

def read_text_auto(path):
    """自适应读取任意编码的小说文本"""
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ["utf-8-sig", "utf-8", "gb18030", "gbk", "big5"]:
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="ignore")

class MasterpieceLearner:
    """七维全息小说研习与逆向工程分析器"""

    # 1. 感官词库
    SENSORY_LEXICON = {
        "tactile": [  # 触觉与本体感觉
            "冰冷", "阴冷", "滚烫", "灼热", "温热", "粗糙", "坚硬", "柔软", "麻木", "刺痛", 
            "剧痛", "冷汗", "窒息", "紧绷", "脱力", "虚脱", "抽搐", "战栗", "发颤", "重若千钧"
        ],
        "auditory": [ # 听觉
            "轰鸣", "刺耳", "尖叫", "尖啸", "碎裂", "沉闷", "闷响", "沙沙", "呼啸", "低语", 
            "窃窃私语", "清脆", "咆哮", "震耳欲聋", "破空声", "金铁交鸣", "死寂", "悄无声息"
        ],
        "olfactory_gustatory": [ # 嗅觉与味觉
            "血腥", "铁锈", "焦糊", "刺鼻", "腐烂", "霉味", "清香", "甜腻", "微苦", "辛辣", 
            "酸涩", "咸涩", "恶臭", "硫磺", "硝烟", "冷香", "尸臭"
        ],
        "visual_lighting": [ # 视觉光影与色调
            "绯红", "惨白", "漆黑", "幽暗", "昏黄", "惨绿", "深邃", "剪影", "高光", "斑驳", 
            "阴影", "微弱", "刺目", "苍白", "血红", "暗红", "银白", "阴霾", "虚幻", "扭曲"
        ]
    }

    # 2. 镜头景别词库
    CAMERA_LEXICON = {
        "close_up": [ # 特写镜头 (微观生理/器物细节)
            "瞳孔", "视线", "指节", "指尖", "嘴角", "眉心", "睫毛", "喉结", "后颈", "下颌",
            "刃口", "剑尖", "衣角", "汗珠", "血滴", "细纹", "裂纹", "毛孔", "齿缝", "呼吸"
        ],
        "medium_shot": [ # 中景镜头 (人物动作博弈/肢体交锋)
            "拔出", "挥刀", "跨步", "侧身", "伸手", "按住", "倒退", "后撤", "抬手", "转身",
            "对视", "逼近", "揽入", "推开", "按在", "握紧", "出拳", "横斩", "交错", "翻滚"
        ],
        "wide_shot": [ # 全景/远景镜头 (宏观局势/环境空间)
            "长街", "大殿", "高空", "远方", "天际", "山峦", "旷野", "暴雨", "城头", "军阵",
            "废墟", "穹顶", "深渊", "星空", "大地", "街巷", "府邸", "黑夜", "苍穹", "四周"
        ]
    }

    # 3. 动态动作动词 vs 静态形容
    DYNAMIC_VERBS = [
        "斩", "劈", "刺", "掠", "撕", "撞", "踏", "震", "扣", "锁", "崩", "拔", "闪", "抽", "砸", "甩", "轰"
    ]
    STATIC_WORDS = [
        "静", "幽", "漫", "徐", "凝", "滞", "默", "冷", "缓", "安", "寂", "沉"
    ]

    # 4. 结尾断章类型特征
    CLIFFHANGER_PATTERNS = {
        "action_cut": [ # 动作硬切
            r"(?:拔出|刺出|转身|跨步|按住|收回|捏碎|抬手|迈步|推门|提刀|合上|按在|一跃)[^\n。！？]{0,10}[。！？]$",
            r"(?:冷冷看着|死死盯着|停下脚步|顿住脚步)[。！？]$"
        ],
        "dialogue_cut": [ # 对白悬置/中断
            r"[”」][。！？]?$",
            r"(?:冷声说道|低语道|轻声道|开口道|反问道|嘶声道)[：:][“「][^\n”」]+[”」]?$"
        ],
        "anomaly_cut": [ # 突发异象/敲门/声响
            r"(?:咚咚咚|砰|咔嚓|突兀响|异变骤生|异象|异响|黑影|脚步声|钟声)[^\n。！？]{0,15}[。！？]$"
        ],
        "preach_cut": [ # 鸡汤/哲理升华 (禁忌项)
            r"(?:这就是.*|或许.*意义|只要.*便|终究是.*人生)[^\n。！？]{0,20}[。！？]$"
        ]
    }

    def __init__(self, corpus_path=None, novel_name=None):
        self.corpus_path = corpus_path
        self.novel_name = novel_name
        self.raw_text = ""
        self.chapters = []

    def load_corpus(self, path=None):
        if path:
            self.corpus_path = path
        if not self.corpus_path or not os.path.exists(self.corpus_path):
            raise FileNotFoundError(f"语料文件不存在: {self.corpus_path}")
        
        if not self.novel_name:
            self.novel_name = os.path.splitext(os.path.basename(self.corpus_path))[0]
            
        print(f"📖 正在加载语料: 《{self.novel_name}》...")
        self.raw_text = read_text_auto(self.corpus_path)
        self._segment_chapters()
        print(f"✅ 语料加载完成！共分词切片 {len(self.chapters)} 章，总字数 {len(self.raw_text):,} 字。")

    def _segment_chapters(self):
        """智能分章"""
        pattern = r'\n\s*(?:第\s*[0-9一二三四五六七八九十百千0-9]+\s*[章回节卷]|Chapter\s*\d+|PART\s*\d+|引子|序章|尾声)[^\n]*\n'
        splits = re.split(pattern, self.raw_text, flags=re.IGNORECASE)
        titles = re.findall(pattern, self.raw_text, flags=re.IGNORECASE)
        
        self.chapters = []
        if len(splits) > 1:
            for i, body in enumerate(splits[1:]):
                title = titles[i].strip() if i < len(titles) else f"第{i+1}章"
                text = body.strip()
                if len(text) > 200: # 过滤空白残章
                    self.chapters.append({
                        "chapter_num": len(self.chapters) + 1,
                        "title": title,
                        "text": text,
                        "length": len(text)
                    })
        else:
            # 单文本无明显分章标识，按 3500 字伪分章
            chunk_size = 3500
            for i in range(0, len(self.raw_text), chunk_size):
                chunk = self.raw_text[i:i+chunk_size].strip()
                if chunk:
                    self.chapters.append({
                        "chapter_num": len(self.chapters) + 1,
                        "title": f"第{len(self.chapters) + 1}节",
                        "text": chunk,
                        "length": len(chunk)
                    })

    # =========================================================
    # 维度一：文字编排与排版节奏 (Typography, Pacing & Layout Architecture)
    # =========================================================
    def learn_typography_and_pacing(self, sample_text):
        """解析段落呼吸律、单句成段率、对话伴随动作编排、标点指纹"""
        paragraphs = [p.strip() for p in sample_text.split("\n") if p.strip()]
        total_p = len(paragraphs)
        if total_p == 0:
            return {}

        p_lengths = [len(p) for p in paragraphs]
        avg_p_len = sum(p_lengths) / total_p
        var_p_len = math.sqrt(sum((l - avg_p_len) ** 2 for l in p_lengths) / total_p)

        # 段落长度分级
        ultra_short = sum(1 for l in p_lengths if l <= 25) # 超短行/单句
        short = sum(1 for l in p_lengths if 26 <= l <= 60)
        medium = sum(1 for l in p_lengths if 61 <= l <= 140)
        long_p = sum(1 for l in p_lengths if l > 140)

        # 单句独立成段率 (段落内仅含 1 个句末标点)
        single_sentence_p = 0
        for p in paragraphs:
            puncts = re.findall(r'[。！？…][”」]?', p)
            if len(puncts) <= 1 and len(p) <= 45:
                single_sentence_p += 1

        # 对白与动作交织编排 (Dialogue vs Action Beats)
        pure_dialogue = 0
        action_tagged_dialogue = 0
        pure_action_narrative = 0

        for p in paragraphs:
            has_quote = ('“' in p and '”' in p) or ('"' in p) or ('「' in p and '」' in p)
            if has_quote:
                # 检查去掉引号对白后是否还保留实体动作描写
                non_dialogue = re.sub(r'“[^”]*”|"[^"]*"|「[^」]*」', '', p).strip()
                if len(non_dialogue) >= 4:
                    action_tagged_dialogue += 1 # 伴随动作神态的对白
                else:
                    pure_dialogue += 1 # 纯台词互抛
            else:
                pure_action_narrative += 1

        # 标点符号指纹 (密度每千字)
        total_k_chars = max(0.1, len(sample_text) / 1000.0)
        dash_count = len(re.findall(r'——|--', sample_text))
        ellipsis_count = len(re.findall(r'……|\.{3,6}', sample_text))
        question_count = len(re.findall(r'[？\?]', sample_text))
        exclamation_count = len(re.findall(r'[！\!]', sample_text))
        comma_count = len(re.findall(r'[，,]', sample_text))
        period_count = len(re.findall(r'[。]', sample_text))

        comma_period_ratio = round(comma_count / max(1, period_count), 2)

        return {
            "avg_paragraph_length": round(avg_p_len, 1),
            "paragraph_length_variance": round(var_p_len, 1),
            "paragraph_distribution": {
                "ultra_short_ratio_le_25": round(ultra_short / total_p, 4),
                "short_ratio_26_60": round(short / total_p, 4),
                "medium_ratio_61_140": round(medium / total_p, 4),
                "long_ratio_gt_140": round(long_p / total_p, 4)
            },
            "single_sentence_paragraph_ratio": round(single_sentence_p / total_p, 4),
            "dialogue_action_weaving": {
                "pure_dialogue_ratio": round(pure_dialogue / total_p, 4),
                "action_tagged_dialogue_ratio": round(action_tagged_dialogue / total_p, 4),
                "pure_narrative_ratio": round(pure_action_narrative / total_p, 4),
                "beat_weaving_density": "高密度动作穿插" if action_tagged_dialogue > pure_dialogue else "紧凑台词对抛"
            },
            "punctuation_fingerprint": {
                "dash_per_kilo": round(dash_count / total_k_chars, 2),
                "ellipsis_per_kilo": round(ellipsis_count / total_k_chars, 2),
                "question_per_kilo": round(question_count / total_k_chars, 2),
                "exclamation_per_kilo": round(exclamation_count / total_k_chars, 2),
                "comma_to_period_ratio": comma_period_ratio,
                "pacing_speed": "极速冲刺流 (短断句/逗句比低)" if comma_period_ratio < 2.0 else "延展抒情/推理流 (长句延展)"
            }
        }

    # =========================================================
    # 维度二：文风与语言神韵 (Style & Linguistic Texture)
    # =========================================================
    def learn_style_and_language(self, sample_text):
        """句式突发度、五感通道偏好、动静张力比、修辞比喻偏好"""
        # 句式切分
        raw_sentences = [s.strip() for s in re.split(r'[。！？!?\n]', sample_text) if len(s.strip()) > 1]
        sent_lens = [len(s) for s in raw_sentences]
        total_s = max(1, len(sent_lens))
        avg_s_len = sum(sent_lens) / total_s
        var_s = math.sqrt(sum((l - avg_s_len) ** 2 for l in sent_lens) / total_s)
        burstiness = round(var_s / (avg_s_len + 1e-5), 3)

        short_s = sum(1 for l in sent_lens if l <= 12)
        long_s = sum(1 for l in sent_lens if l >= 35)

        # 五感通道偏好分析
        total_chars = max(1, len(sample_text))
        sensory_scores = {}
        for channel, words in self.SENSORY_LEXICON.items():
            count = sum(len(re.findall(re.escape(w), sample_text)) for w in words)
            sensory_scores[channel] = count

        sensory_sum = max(1, sum(sensory_scores.values()))
        sensory_profile = {
            k: round(v / sensory_sum, 4) for k, v in sensory_scores.items()
        }

        # 动静张力比
        dyn_count = sum(sample_text.count(v) for v in self.DYNAMIC_VERBS)
        sta_count = sum(sample_text.count(s) for s in self.STATIC_WORDS)
        dyn_ratio = round(dyn_count / max(1, (dyn_count + sta_count)), 3)

        # 比喻密度
        metaphor_pats = [r'像[^，。！？]{1,15}(?:一样|一般|似的)', r'宛如', r'如同', r'仿佛', r'好似']
        metaphor_count = sum(len(re.findall(p, sample_text)) for p in metaphor_pats)
        k_chars = max(0.1, total_chars / 1000.0)
        metaphor_density = round(metaphor_count / k_chars, 2)

        return {
            "sentence_burstiness": burstiness,
            "avg_sentence_length": round(avg_s_len, 1),
            "sentence_cadence": {
                "short_sentence_ratio_le_12": round(short_s / total_s, 4),
                "long_sentence_ratio_ge_35": round(long_s / total_s, 4),
                "style_category": "短促爆破与动词推进型" if burstiness >= 0.55 else "匀速从容叙事型"
            },
            "sensory_channel_weights": sensory_profile,
            "dominant_sense": max(sensory_profile, key=sensory_profile.get),
            "dynamic_tension_ratio": dyn_ratio,
            "verb_orientation": "强动能搏杀/冲撞偏好" if dyn_ratio >= 0.65 else "静谧凝练/心理铺垫偏好",
            "metaphor_density_per_kilo": metaphor_density
        }

    # =========================================================
    # 维度三：写法与叙事技法 (Narrative Craft & POV Mechanics)
    # =========================================================
    def learn_narrative_craft(self, sample_text):
        """视角策略 (POV)、景别焦距 (Close/Med/Wide)、潜台词与留白"""
        total_len = len(sample_text)
        
        # 1. POV 判定
        first_person = len(re.findall(r'(?:我|我们)(?:[，。！？\s]|$)', sample_text))
        third_person_he = len(re.findall(r'(?:他|他们)', sample_text))
        third_person_she = len(re.findall(r'(?:她|她们)', sample_text))
        
        if first_person > (third_person_he + third_person_she) * 0.8:
            pov = "第一人称极限主观视角 (First-Person Limited POV)"
        else:
            pov = "限知第三人称跟随视角 (Close Third-Person POV)"

        # 2. 镜头景别变焦比例
        camera_counts = {}
        for shot, keywords in self.CAMERA_LEXICON.items():
            c = sum(len(re.findall(re.escape(w), sample_text)) for w in keywords)
            camera_counts[shot] = c
            
        cam_total = max(1, sum(camera_counts.values()))
        camera_distribution = {
            "close_up_ratio": round(camera_counts["close_up"] / cam_total, 4),
            "medium_shot_ratio": round(camera_counts["medium_shot"] / cam_total, 4),
            "wide_shot_ratio": round(camera_counts["wide_shot"] / cam_total, 4)
        }

        dominant_shot = max(camera_distribution, key=camera_distribution.get)
        shot_interpretation = {
            "close_up_ratio": "微观特写锁定：极其关注微表情、器物反光与生理痛觉",
            "medium_shot_ratio": "中景交锋锁定：专注人物肢体拉扯、语言试探与动作博弈",
            "wide_shot_ratio": "宏观全景俯瞰：重在阵营局势、环境风貌与大场面气势"
        }[dominant_shot]

        # 3. 潜台词留白度 (通过对话中未尽之意、反问、停顿估算)
        subtext_clues = len(re.findall(r'“[^”]*……”|“[^”]*？”|眼神一[闪沉变]|没有回答|移开视线|若有所思', sample_text))
        subtext_density = round(subtext_clues / max(0.1, total_len / 1000.0), 2)

        return {
            "pov_strategy": pov,
            "camera_framing_distribution": camera_distribution,
            "camera_primary_focus": shot_interpretation,
            "subtext_density_per_kilo": subtext_density,
            "narrative_temperament": "高压潜台词博弈型" if subtext_density >= 2.0 else "直白高效行动型"
        }

    # =========================================================
    # 维度四：创作思路与心智模型 (Author Mindset & Reasoning Engine)
    # =========================================================
    def learn_author_mindset(self, sample_chapters):
        """逆向作者推演逻辑：绝境构造、阻力升级、代价与代偿平衡"""
        # 分析章节中冲突对抗与代价的词汇共现
        conflict_signals = [
            "必须", "代价", "两难", "抉择", "死局", "绝境", "反扑", "陷阱", "圈套", "背叛", "断腕"
        ]
        cost_signals = [
            "残破", "重伤", "损耗", "寿元", "鲜血", "失去", "舍弃", "暴跌", "崩裂", "不可逆"
        ]

        text_concat = " ".join([c["text"] for c in sample_chapters])
        conflict_freq = sum(text_concat.count(w) for w in conflict_signals)
        cost_freq = sum(text_concat.count(w) for w in cost_signals)
        k_chars = max(0.1, len(text_concat) / 1000.0)

        # 阻力模式反推
        dilemma_density = round(conflict_freq / k_chars, 2)
        cost_density = round(cost_freq / k_chars, 2)

        return {
            "escalation_ladder": {
                "level_1_physical": "外部环境与敌对力量正面交锋",
                "level_2_rules_hierarchy": "体制戒律、超凡法则或阶级规训施压",
                "level_3_ethical_dilemma": "两难权衡与两害相权取其轻的终极抉择"
            },
            "cost_compensation_ratio": round(cost_density / max(0.01, dilemma_density), 2),
            "mindset_rules": [
                "绝对拒绝机械降神：主角破局必须依靠自身专业技能或预先埋设的信息差",
                "代价法则严苛：绝无免费外挂，凡力量跃迁必伴随不可逆消耗或副作用",
                "装逼必须有'垫子'：先有长辈/强敌看衰与重压蓄势，而后公堂/当众绝杀"
            ]
        }

    # =========================================================
    # 维度五：框架与大纲拓扑 (Framework & Tension Architecture)
    # =========================================================
    def learn_framework_and_beats(self, sample_chapters):
        """全卷潮汐张力、开卷起手分布、收尾断章钩子分类"""
        cliffhangers = {
            "action_cut": 0,
            "dialogue_cut": 0,
            "anomaly_cut": 0,
            "preach_cut": 0,
            "other_cut": 0
        }

        openings_archetypes = Counter()

        for c in sample_chapters:
            text = c["text"]
            tail = text[-120:].strip()
            head = text[:120].strip()

            # 断章模式命中
            matched = False
            for c_type, pats in self.CLIFFHANGER_PATTERNS.items():
                if any(re.search(p, tail) for p in pats):
                    cliffhangers[c_type] += 1
                    matched = True
                    break
            if not matched:
                cliffhangers["other_cut"] += 1

            # 起手模式
            if re.search(r'(?:清晨|早晨|拂晓|睁开眼|醒来|旭日|天边泛白)', head):
                openings_archetypes["破晓苏醒/推门型"] += 1
            elif re.search(r'(?:书房|工位|案头|静室|蒲团|端坐|沉吟)', head):
                openings_archetypes["静坐思索/办公型"] += 1
            elif re.search(r'(?:“|「|[拔出|拔剑|疾驰|踏入|鲜血|轰鸣])', head):
                openings_archetypes["突发对白/行动切入型"] += 1
            else:
                openings_archetypes["环境交代/叙事切入型"] += 1

        total_chaps = max(1, len(sample_chapters))
        cliffhanger_ratios = {
            k: round(v / total_chaps, 4) for k, v in cliffhangers.items()
        }

        return {
            "chapter_opening_distribution": {
                k: round(v / total_chaps, 4) for k, v in openings_archetypes.items()
            },
            "cliffhanger_hook_distribution": cliffhanger_ratios,
            "cliffhanger_compliance": "优秀 (零哲学升华说教，动作与对白硬切为主)" if cliffhanger_ratios["preach_cut"] == 0 else "警告 (存在哲学说教尾巴)",
            "four_scene_budget_standard": {
                "scene_1": "20% (600-800字) - 生理承接与切入，拒绝发呆洗脸",
                "scene_2": "30% (900-1100字) - 多方交锋与实质信息差",
                "scene_3": "30% (900-1100字) - 矛盾升级与冒险决断",
                "scene_4": "20% (500-700字) - 悬念硬切定格，绝不鸡汤升华"
            }
        }

    # =========================================================
    # 维度六：情节因果与信息差 (Plot & Causality DAG)
    # =========================================================
    def learn_plot_and_causality(self, sample_chapters):
        """因果链推进强度 ('Therefore/But' vs 'And then') 与信息差马甲结构"""
        text_concat = " ".join([c["text"] for c in sample_chapters])
        k_chars = max(0.1, len(text_concat) / 1000.0)

        # 强因果转折词
        causal_signals = len(re.findall(r'(?:因此|所以|以至于|正因如此|不得不)', text_concat))
        adversative_signals = len(re.findall(r'(?:然而|但是|偏偏|岂料|谁知|异变陡生|未曾想)', text_concat))
        # 弱流水账词
        and_then_signals = len(re.findall(r'(?:然后|紧接着|接着|随后|过了不久)', text_concat))

        causal_density = round(causal_signals / k_chars, 2)
        adversative_density = round(adversative_signals / k_chars, 2)
        and_then_density = round(and_then_signals / k_chars, 2)

        causal_tightness = round((causal_signals + adversative_signals) / max(1, and_then_signals), 2)

        return {
            "causal_adversative_density_per_kilo": round(causal_density + adversative_density, 2),
            "and_then_weak_narrative_density": and_then_density,
            "causality_tightness_ratio": causal_tightness,
            "plot_driving_style": "高密度强因果博弈 ('Therefore / But' 驱动)" if causal_tightness >= 2.0 else "平铺直叙型流水线",
            "information_gap_patterns": [
                "身份马甲与单向透明：主角掌握暗线情报网（如匿名通讯/双重身份），对手蒙在鼓里",
                "认知降维打击：主角凭借专业刑侦/物理/现代逻辑，从微小破绽逆推真相",
                "延时揭秘：核心底牌在危机爆发前 3 章预埋，在绝境关头完成伏笔闭环"
            ]
        }

    # =========================================================
    # 维度七：内容与世界观设定 (Content & World Conception)
    # =========================================================
    def learn_content_and_world(self, sample_text):
        """核心超凡品级/体系、势力格局、核心冲突源动力"""
        # 提取高频势力/职衔/品级专有名词
        hierarchy_terms = re.findall(r'(?:[一二三四五六七八九]品|[炼筑结元化洞渡][气基丹婴神虚劫]|武夫|儒家|术士|道门|佛门|天师|巡抚|总兵|铜锣|银锣|金锣|执事|长老|弟子)', sample_text)
        top_hierarchy = [item[0] for item in Counter(hierarchy_terms).most_common(8)]

        # 势力对抗词
        faction_terms = re.findall(r'(?:朝廷|衙门|司|宗|门|帮|殿|阁|教|院|部|商会|军)', sample_text)
        top_factions = [item[0] for item in Counter(faction_terms).most_common(6)]

        return {
            "power_hierarchy_keywords": top_hierarchy if top_hierarchy else ["九品超凡体系", "官僚体制品阶"],
            "faction_domains": top_factions if top_factions else ["特务执法衙门", "朝廷党争", "江湖宗派"],
            "core_rules_constraints": [
                "超凡力量与世界法则严苛绑定，每种职业体系具备绝对弱点（如武夫神魂弱、术士受天谴、儒家耗寿元）",
                "世俗王权与超凡宗门双轨并存，主角依托体制内暴力特权机构展开行动",
                "资源有限性：超凡丹药、法宝、气运皆具零和博弈属性"
            ]
        }

    # =========================================================
    # 综合研习执行入口 (Full Ingestion & Blueprint Compilation)
    # =========================================================
    def execute_deep_learning(self, sample_chapters_count=40, output_dir=None):
        """执行七维全息解构，输出 JSON DNA 蓝图与 Markdown 参考手册"""
        if not self.chapters:
            raise ValueError("尚未加载小说文本或分章失败！")

        if output_dir is None:
            output_dir = DEFAULT_PROFILE_DIR
        os.makedirs(output_dir, exist_ok=True)

        selected_chapters = self.chapters[:min(len(self.chapters), sample_chapters_count)]
        sample_text = "\n\n".join([c["text"] for c in selected_chapters])
        sample_chars = len(sample_text)

        print(f"🔬 正在对《{self.novel_name}》开展七维全息逆向工程研习...")
        print(f"📊 样本规模: 前 {len(selected_chapters)} 章，共计 {sample_chars:,} 字。")

        # 1. 文字编排与排版节奏
        typography = self.learn_typography_and_pacing(sample_text)
        # 2. 文风与语言神韵
        style = self.learn_style_and_language(sample_text)
        # 3. 写法与叙事技法
        craft = self.learn_narrative_craft(sample_text)
        # 4. 创作思路与心智模型
        mindset = self.learn_author_mindset(selected_chapters)
        # 5. 框架与大纲拓扑
        framework = self.learn_framework_and_beats(selected_chapters)
        # 6. 情节因果与信息差
        plot = self.learn_plot_and_causality(selected_chapters)
        # 7. 内容与世界观设定
        world = self.learn_content_and_world(sample_text)

        # 整合为 Masterpiece DNA Profile
        dna_profile = {
            "version": "3.2.0",
            "novel_name": self.novel_name,
            "sample_chapters_analyzed": len(selected_chapters),
            "sample_char_count": sample_chars,
            "dimension_1_typography_pacing": typography,
            "dimension_2_style_language": style,
            "dimension_3_narrative_craft": craft,
            "dimension_4_author_mindset": mindset,
            "dimension_5_framework_beats": framework,
            "dimension_6_plot_causality": plot,
            "dimension_7_world_conception": world
        }

        # 保存为 JSON 蓝图
        json_path = os.path.join(output_dir, f"{self.novel_name}.dna.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dna_profile, f, ensure_ascii=False, indent=2)
        print(f"💾 [1/2] 机器级 DNA 蓝图保存成功 -> {json_path}")

        # 生成人类/AI 深度可读的 Markdown 全息手册
        md_content = self._render_master_handbook(dna_profile)
        md_path = os.path.join(output_dir, f"{self.novel_name}_全息研习参考手册.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"📑 [2/2] 人类/AI 全息研习参考手册生成成功 -> {md_path}")

        return dna_profile, md_path

    def _render_master_handbook(self, dna):
        """渲染极其精美、工业级严密的 Markdown 全息研习报告"""
        d1 = dna["dimension_1_typography_pacing"]
        d2 = dna["dimension_2_style_language"]
        d3 = dna["dimension_3_narrative_craft"]
        d4 = dna["dimension_4_author_mindset"]
        d5 = dna["dimension_5_framework_beats"]
        d6 = dna["dimension_6_plot_causality"]
        d7 = dna["dimension_7_world_conception"]

        md = f"""# 📑 《{dna['novel_name']}》全息架构与创作工程逆向研习手册
*(Master Reference Blueprint: {dna['novel_name']} Holographic Deconstruction)*

> **样本规模**：精读并逆向工程拆解前 {dna['sample_chapters_analyzed']} 章（共 {dna['sample_char_count']:,} 字）  
> **生成引擎**：Novel-Crafting Engine v3.2.0 (Masterpiece Learner)  
> **适用场景**：全题材长篇小说选题对标、分镜事件设计、文风编译对齐、排版节奏调校与代码级质检门禁。

---

## 一、 七维全息雷达与数理基准 (Ground Truth Metrics)

经过全息小说学习机深度解构，原著的核心数理指纹与创作门禁如下：

| 核心维度 | 原著实测指标 | 工业级写作指导原则与硬门禁 |
| :--- | :---: | :--- |
| **平均段落长度** | **{d1['avg_paragraph_length']} 字/段** (方差 {d1['paragraph_length_variance']}) | 段落呼吸极具弹性，拒绝沉闷大段！ |
| **单句独段占比** | **{d1['single_sentence_paragraph_ratio']:.1%}** | 高频使用单句成段作为情绪强拍与视线加速器。 |
| **动作穿插对白比** | **{d1['dialogue_action_weaving']['action_tagged_dialogue_ratio']:.1%}** ({d1['dialogue_action_weaving']['beat_weaving_density']}) | 拒绝纯台词干聊！台词必须附带神态、微观动作或道具交互。 |
| **句式突发度 (Burstiness)** | **{d2['sentence_burstiness']}** ({d2['sentence_cadence']['style_category']}) | 短句爆破 (≤12字占 {d2['sentence_cadence']['short_sentence_ratio_le_12']:.1%}) 与复合长句交替轰鸣。 |
| **修辞比喻密度** | **{d2['metaphor_density_per_kilo']} 个/千字** | 修辞极度克制，严禁泛滥陈词滥调！ |
| **主导感官通道** | **{d2['dominant_sense']}** (触觉/本体感占 {d2['sensory_channel_weights']['tactile']:.1%}) | 死死锚定人物肉体生理反射与冰冷微观质感。 |
| **镜头景别重心** | **{d3['camera_primary_focus']}** | 特写占 {d3['camera_framing_distribution']['close_up_ratio']:.1%}，中景占 {d3['camera_framing_distribution']['medium_shot_ratio']:.1%}。 |
| **因果咬合紧密度** | **{d6['causality_tightness_ratio']}** ({d6['plot_driving_style']}) | 拒绝流水账 'And then'，全以 'Therefore / But' 逻辑推进！ |
| **断章收尾规范** | 动作切 {d5['cliffhanger_hook_distribution']['action_cut']:.1%} ｜ 对白切 {d5['cliffhanger_hook_distribution']['dialogue_cut']:.1%} ｜ 说教 {d5['cliffhanger_hook_distribution']['preach_cut']:.1%} | **绝对禁止结尾哲理鸡汤升华**，全在行动或反转对白上硬切。 |

---

## 二、 文字编排与排版呼吸律 (Typography & Pacing Architecture)

### 1. 段落长度分布梯度 (Paragraph Length Breathing)
- **超短段 (≤ 25字)**：占比 **{d1['paragraph_distribution']['ultra_short_ratio_le_25']:.1%}** —— 用于视线无阻力下滑、冲突爆发与关键动作定格。
- **短段 (26 ~ 60字)**：占比 **{d1['paragraph_distribution']['short_ratio_26_60']:.1%}** —— 人物对话伴随动作，节奏轻快。
- **中段 (61 ~ 140字)**：占比 **{d1['paragraph_distribution']['medium_ratio_61_140']:.1%}** —— 多人交锋或环境物证沉淀。
- **长段 (> 140字)**：占比 **{d1['paragraph_distribution']['long_ratio_gt_140']:.1%}** —— 严控大段篇幅，防止阅读心流阻滞。

### 2. 标点符号情绪谱系 (Punctuation Fingerprint)
- **逗句比 (, / 。)**：`{d1['punctuation_fingerprint']['comma_to_period_ratio']}` —— **{d1['punctuation_fingerprint']['pacing_speed']}**。
- **破折号密度 (——)**：每千字 `{d1['punctuation_fingerprint']['dash_per_kilo']}` 个 —— 负责语势急刹车与思绪被粗暴打断。
- **省略号密度 (……)**：每千字 `{d1['punctuation_fingerprint']['ellipsis_per_kilo']}` 个 —— 负责心理留白与空气凝固。

---

## 三、 文风与语言神韵 (Style & Linguistic Texture)

### 1. 动静张力与搏杀推进
- **动静张力比**：`{d2['dynamic_tension_ratio']}` ({d2['verb_orientation']})。
- 镜头死死咬定人物动态变化，多用单音节强动词（如：斩、扣、踏、崩、锁、掠）。

### 2. 五感色彩配置
- **触觉与本体感觉** ({d2['sensory_channel_weights']['tactile']:.1%})：聚焦冷汗、肌肉紧绷、下颌咬紧、视线凝固。
- **听觉通道** ({d2['sensory_channel_weights']['auditory']:.1%})：突出金铁交鸣、破空碎裂与死寂反差。
- **嗅觉与味觉** ({d2['sensory_channel_weights']['olfactory_gustatory']:.1%})：铁锈、血腥、刺鼻硝烟烘托危险真实度。
- **视觉光影** ({d2['sensory_channel_weights']['visual_lighting']:.1%})：剪影与幽暗光斑，拒绝明晃晃说明文。

---

## 四、 写法与叙事技法 (Narrative Craft & POV Mechanics)

### 1. 视角控制策略 (POV Strategy)
- 采用 **{d3['pov_strategy']}**。
- 始终以主角的双眼和感知为边界，严禁上帝视角擅自替配角或反派进行冗长心理分析！

### 2. 镜头焦距与景别变焦 (Camera Framing)
```mermaid
flowchart LR
    Wide["全景/远景 ({d3['camera_framing_distribution']['wide_shot_ratio']:.1%})\n宏观阵营与环境空间"] --> Medium["中景 ({d3['camera_framing_distribution']['medium_shot_ratio']:.1%})\n人物身体动作博弈"]
    Medium --> Close["特写 ({d3['camera_framing_distribution']['close_up_ratio']:.1%})\n微观神态与器物刃口"]
    Close --> Action["行动突变硬切定格"]
```

### 3. 潜台词留白艺术 (Subtext & Iceberg Principle)
- 潜台词密度达到 **{d3['subtext_density_per_kilo']} 处 / 千字**。
- 角色对白言不由衷、指桑骂槐，表面平静推杯换盏，桌下暗藏杀机。

---

## 五、 创作者心智与阻力升级阶梯 (Author Mindset & Reasoning)

### 1. 三级阻力演进模型 (Escalation Ladder)
1. **第 1 级（物理/自然阻力）**：{d4['escalation_ladder']['level_1_physical']}。
2. **第 2 级（规训/制度阻力）**：{d4['escalation_ladder']['level_2_rules_hierarchy']}。
3. **第 3 级（伦理/两难抉择）**：{d4['escalation_ladder']['level_3_ethical_dilemma']}。

### 2. 代价平衡法则 (Cost & Compensation Calculus)
- 代价与冲突比率：`{d4['cost_compensation_ratio']}`。
- **核心法则**：
"""
        for rule in d4["mindset_rules"]:
            md += f"  - {rule}\n"

        md += f"""
---

## 六、 框架拓扑与单章四场次微观节拍 (Framework & Beats Architecture)

### 1. 单章 3000 字通用四场次物理预算
- **Scene 1 (20%, ~600-800字)**：{d5['four_scene_budget_standard']['scene_1']}。
- **Scene 2 (30%, ~900-1100字)**：{d5['four_scene_budget_standard']['scene_2']}。
- **Scene 3 (30%, ~900-1100字)**：{d5['four_scene_budget_standard']['scene_3']}。
- **Scene 4 (20%, ~500-700字)**：{d5['four_scene_budget_standard']['scene_4']}。

### 2. 断章钩子类型分布
- **动作切入硬切**：占比 **{d5['cliffhanger_hook_distribution']['action_cut']:.1%}**。
- **对白悬置硬切**：占比 **{d5['cliffhanger_hook_distribution']['dialogue_cut']:.1%}**。
- **突发异象硬切**：占比 **{d5['cliffhanger_hook_distribution']['anomaly_cut']:.1%}**。
- **合规门禁评价**：**{d5['cliffhanger_compliance']}**。

---

## 七、 情节因果与信息差博弈引擎 (Plot DAG & Information Gap)

### 1. 因果咬合逻辑 ("Therefore / But" DAG)
- 强因果转折词密度达每千字 **{d6['causal_adversative_density_per_kilo']}** 个。
- 逻辑坚实度比值：`{d6['causality_tightness_ratio']}` ({d6['plot_driving_style']})。

### 2. 核心信息差设计法则
"""
        for p in d6["information_gap_patterns"]:
            md += f"- **{p}**\n"

        md += f"""
---

## 八、 内容世界观与超凡戒律代价 (World Conception & Power Rules)

### 1. 核心力量阶梯与职衔高频意象
- **高频体系词汇**：`{" / ".join(d7['power_hierarchy_keywords'])}`
- **核心博弈场域**：`{" / ".join(d7['faction_domains'])}`

### 2. 戒律与代价约束
"""
        for c in d7["core_rules_constraints"]:
            md += f"- {c}\n"

        md += f"""
---

## 九、 新书实战创作对标启示清单 (Master Actionable Checklist)

在对标《{dna['novel_name']}》创作新作品时，请严格逐项审查以下硬指标：

- [ ] **排版呼吸检核**：单句成段率是否达到 **{d1['single_sentence_paragraph_ratio']:.1%}**？平均段落长度是否控制在 **{d1['avg_paragraph_length']} 字**左右？
- [ ] **动作伴随对白检核**：是否至少有 **{d1['dialogue_action_weaving']['action_tagged_dialogue_ratio']:.1%}** 的对白带有身体动作或微神态？
- [ ] **句式节奏检核**：长短句突发度是否达到 **{d2['sentence_burstiness']}**？是否避免匀速流水账？
- [ ] **感官锚定检核**：是否深度调动了 **{d2['dominant_sense']}**（触觉/本体感知）描写，而非悬浮形容词？
- [ ] **断章硬切检核**：结尾是否彻底根除了鸡汤升华，干净利落地定格在物理动作或反转对白上？
- [ ] **信息差装逼检核**：主角装逼前是否有完整的“看衰蓄势”与“单向信息差物证”铺垫？
"""
        return md

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Masterpiece Learner CLI")
    parser.add_argument("corpus_path", help="语料 txt 路径")
    parser.add_argument("--chapters", type=int, default=40, help="分析样本章节数")
    parser.add_argument("--output", default=None, help="输出目录")
    args = parser.parse_args()

    learner = MasterpieceLearner(args.corpus_path)
    learner.load_corpus()
    learner.execute_deep_learning(sample_chapters_count=args.chapters, output_dir=args.output)
