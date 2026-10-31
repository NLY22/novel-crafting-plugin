# Claude Code (cc) 专属长篇小说辅助创作指令指南 (Novel-Crafting Protocol)

当在 Claude Code (`cc`) 终端或子代理中进行中文长篇小说创作、大纲规划、章节续写或代码级质检时，必须无条件遵循以下工业级流水线规范：

---

## 🚫 核心禁令：剥夺黑盒端到端直出正文权限
严禁直接向模型发送“写第 X 章”并一口气生成全章草稿！
必须严格执行 **Two-Pass 叙事驱动与文风解耦流水线**：

### 阶段 1：Pass 1 剧力推进与事件骨架断言
在动笔前，运行 `core/narrative_engine.py` 规划本章分镜事件卡并执行物理断言：
- **核心事件**：本章是否存在至少一个改变人物处境或心理状态的核心事件？
- **戏剧阻力**：若是日常过渡，其外部阻力与冲突变量是什么？
- **信息差**：在场人物之间是否存在认知不对称与试探潜台词？
- **四场次物理预算**：Scene 1 (20%, ~700字) 生理切入 -> Scene 2 (30%, ~1000字) 对白交锋 -> Scene 3 (30%, ~1000字) 矛盾升级 -> Scene 4 (20%, ~600字) 断章硬切。
- **创作者确认**：分镜事件卡输出后，必须获得创作者拍板，方可进入 Pass 2！

### 阶段 2：Pass 2 文风特征渲染编译
创作者确认后，运行 `core/prompt_builder.py` 编译作家专属 Few-Shot 指令（顾漫流/狐尾流/卖报流）：
- 注入原著开篇入局切片与对白机锋示范；
- 落实作家专属手艺（括号轻吐槽、颠倒生理错乱、市井骚话反咬）；
- 封杀作家专属违规笔调（公文腔、无脑装逼打脸、圣母鸡汤）。

### 阶段 3：代码级 Micro Linter 与 Auto-Healer 自愈闭环
正文生成后，运行 `core/novel_linter.py` 执行静态审查：
- 严禁“钻心的痛/心中一紧/倒吸凉气/瞳孔骤缩/眼前发黑”等抽象情绪词；
- 严禁段末/章末人生导师式哲学说教（“这就是人生/只要...就总有...”）；
- 比喻密度严格 $\le 2.5$ 个/千字，景物注水率严格 $\le 15\%$，长短句突发度 $\ge 0.60$；
- 若评分未达 100 分，自动调用 `core/auto_healer.py` 定向物理化代换自愈至 100 分。

---

## 🛠️ Claude Code 常用执行命令速查

```bash
# 1. 运行微观 Universal Linter 质检
python core/novel_linter.py

# 2. 运行 Auto-Healer 一键满分自愈
python core/auto_healer.py

# 3. 运行跨章反土拨鼠纵向审查
python core/longitudinal_linter.py

# 4. 查询到期暗线与时间锁
python -c "from core.plot_tracker import PlotTracker; PlotTracker().get_due_reminders(当前章号)"

# 5. 查看 World State Ledger 因果状态机简报 (防吃书)
python core/world_state_ledger.py

# 6. 十字路口 A/B/C 三走向推演
python core/branching_generator.py
```
