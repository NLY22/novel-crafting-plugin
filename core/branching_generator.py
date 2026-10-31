# -*- coding: utf-8 -*-
"""
戏剧多分支推演引擎 (Branching Scenario Generator) - Plugin Core Module
自适应相对路径，无任何外部硬编码。
"""

import sys
import io

if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def generate_branches(scene_context, current_objective):
    print("=" * 65)
    print(" 🎲 【戏剧分叉路口】正在基于当前局势推演 3 大走向分支...")
    print("=" * 65)
    print(f"当前现场情境: {scene_context}")
    print(f"当前核心诉求: {current_objective}")
    print("-" * 65)

    branches = [
        {
            "id": "A",
            "name": "【强冲突·危机激化流】",
            "tension_level": "⭐⭐⭐⭐⭐ (极高烈度)",
            "mechanism": "将矛盾当场引爆，强行打破表面平衡，付出不可逆的惨烈代价。",
            "synopsis": "角色放弃退路，直接利用眼前的破绽对目标进行正面斩首或极限施压。局势瞬间失控，必须在一分钟内决定生死。",
            "pros": "爽点集中，情绪爆发力强，能瞬间抓住读者眼球。",
            "cons": "底牌过早暴露，后续需要面临全观通缉或同伴反目等严苛后遗症。"
        },
        {
            "id": "B",
            "name": "【暗流涌动·心理博弈流】(经典风骨)",
            "tension_level": "⭐⭐⭐⭐ (深层压迫)",
            "mechanism": "表面极尽顺从赔笑，实则在对白和微动作中暗布杀机，借刀杀人。",
            "synopsis": "装作完全不知情或弱势方，故意抛出虚假或半真半假的信息诱饵，引导敌对势力之间互相猜忌火并，主角隐忍坐收渔利。",
            "pros": "智斗感极强，市井生存哲学浓厚，符合主角受限条件下的自保逻辑。",
            "cons": "推进节奏较为收敛，需要作者极精细地打磨台词潜台词。"
        },
        {
            "id": "C",
            "name": "【荒诞撕裂·认知颠覆流】",
            "tension_level": "⭐⭐⭐⭐⭐ (惊悚绝伦)",
            "mechanism": "突发第三方异常变量，或让主角的隐秘心理/幻觉世界在最致命时刻与现实重叠。",
            "synopsis": "主角在关键动作的一瞬间，突然视线撕裂，发现眼前致命的对手变成了现实中的亲人或荒诞道具；或者发现争夺的目标本身就是个巨大的荒诞骗局。",
            "pros": "极具特异性文学冲击力，彻底拉开与普通凡俗网文的档次差距。",
            "cons": "对心理抗压描写要求极高，用得不好容易打断当前的打斗节奏。"
        }
    ]

    for b in branches:
        print(f"\n👉 分支 {b['id']}: {b['name']} | 张力: {b['tension_level']}")
        print(f"   【核心机制】: {b['mechanism']}")
        print(f"   【剧情脉络】: {b['synopsis']}")
        print(f"   【优势评估】: {b['pros']}")
        print(f"   【潜在代价】: {b['cons']}")

    print("\n" + "=" * 65)
    print("💡 导演选择提示: 确定心仪分支后，系统将仅围绕该分支展开正文。")
    return branches

class BranchingGenerator:
    def generate(self, scene_context, current_objective):
        return generate_branches(scene_context, current_objective)

if __name__ == "__main__":
    context = "主角站在关键路口，身后有追兵，眼前只有一条看似通往深渊的小道。"
    objective = "如何抉择？"
    generate_branches(context, objective)
