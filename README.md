# 📖 NovelCrafting-Plugin 工业级通用小说创作引擎 (v3.0.0)

> 一款工业级、全题材解耦的中文长篇小说辅助创作与“去 AI 塑料味”双层流水线插件引擎。  
> 🌟 **全生态原生兼容**：原生适配 **Claude Code (`cc`)**、**DeepSeek Harness (`dsh`)**、**OpenAI Codex (`codex`)**、**Google Antigravity (`agy`)**、**Cursor / Windsurf** 以及 **Obsidian 本地知识库**。

---

## 🌟 核心解决的问题与教训

在长篇中文小说辅助创作中，传统 AI 往往存在以下致命病灶：
1. **文风与叙事混淆（流水账打卡病）**：以为套用名家遣词造句就是好小说，结果写出 1,000 字毫无剧情推进的慢镜头打坐、采药、吃早餐、点烟叹气；
2. **AI 恶俗词与悬浮情绪泛滥**：“钻心的痛”、“痛彻心扉”、“像生锈的冰锥”、“心中一紧/一震”、“倒吸凉气”、“瞳孔骤缩”满天飞；
3. **人生导师式强行升华**：每段末尾或章末必须感慨一句“只要……就总有一天会……”，充斥着学生范文和鸡汤说教味；
4. **单章字数营养不良与无意义独白注水**：一次性只吐出 1,200~1,500 字仓促大纲式正文，缺乏商业小说 3,000 字所必需的微观博弈与四场次呼吸；
5. **跨章节“土拨鼠之日”同质化**：每章开篇都在看窗外/吃早餐，每章结尾都在端茶杯/陷入沉思；
6. **超长程因果失忆（吃书）**：写到第 20 章，完全忘记第 3 章留下的生理伤势、随身余银，甚至 NPC 杀意反常归零。

**NovelCrafting-Plugin 采用 Two-Pass 叙事驱动与文风渲染双层解耦架构、跨章节反土拨鼠审查、因果状态机、Auto-Healer 自愈闭环及标准 MCP Server，彻底根治以上所有顽疾。**

---

## 🌐 跨生态全 Agent 原生兼容支持 (Codex / DSH / CC / Cursor / Antigravity)

本插件经过专门工程化重构，无需任何二次修改，一套核心代码直接通吃主流 Coding Agent 运行环境：

| AI 运行环境 / 终端 | 挂载与识别机制 | 自动化支持与生效路径 |
| :--- | :--- | :--- |
| **Claude Code (`cc`)** | `SKILL.md` + `CLAUDE.md` + `MCP Server` | 自动写入 `~/.claude/skills/novel-crafting/`，支持 `/novel-crafting` 技能唤醒与原生 MCP 工具调用 |
| **DeepSeek Harness (`dsh`)** | `package.json` + `Cordis Plugin` + `SKILL.md` | 自动挂载至 `~/.agents/skills/novel-crafting/`，符合 DSH 官方插件包与技能标准 |
| **OpenAI Codex / CLI** | `AGENTS.md` + `SKILL.md` + 标准 CLI | 根目录与 `~/.codex/` 部署全局行为准则，强制执行 Two-Pass 与代码级门禁 |
| **Google Antigravity (`agy`)** | `plugin.json` + `rules/AGENTS.md` + 技能系统 | 自动同步至 `~/.gemini/config/plugins/novel-crafting/`，实时热重载 |
| **Cursor / Windsurf IDE** | `.cursorrules` + 命令行工具箱 | 工作区根目录植入物理门禁，AI 编辑正文时实时执行代码审查 |
| **Obsidian 本地离线环境** | 双击批处理 + Markdown 模板 | 双击 `启动助手.bat` 呼出 13 选 1 图形控制台，零安装即开即用 |

### ⚡ 一键分发至全生态：
直接双击根目录下的 **`一键安装到所有AI终端.bat`**（或终端运行 `python install_universal.py`），脚本将自动扫描并一键把插件挂载到本机的 Claude Code、DeepSeek Harness、Codex 及 Antigravity 中！

---

## 🗂️ 插件目录架构 (全相对路径，零安装零外置依赖)

```text
NovelCrafting-Plugin/
├── 📄 plugin.json                 ← Antigravity / Gemini 官方插件声明 (v3.0.0)
├── 📄 package.json                ← DeepSeek Harness (DSH) / Cordis 插件包声明
├── 📄 SKILL.md                     ← 通用 Agent 技能规范 (CC / DSH / AGY / Codex 共享)
├── 📄 CLAUDE.md                    ← Claude Code (cc) 专属项目指令规范
├── 📄 AGENTS.md                    ← OpenAI Codex 顶层通用行为法则与门禁
├── 📄 .cursorrules                 ← Cursor / Windsurf IDE 静态质检规则
├── 📄 mcp_server.py                ← 🌟 跨平台标准 MCP 服务 (零依赖纯 Python 实现)
├── 📄 install_universal.py         ← 🌟 跨 Agent 一键全平台分发安装脚本
├── 🚀 一键安装到所有AI终端.bat      ← Windows 双击一键分发入口
├── 🚀 启动助手.bat                 ← Windows 便携双击交互入口
├── ⚙️ 启动助手.ps1                 ← 交互控制台主逻辑 (13 选 1 极速面板)
│
├── 📂 core/                        ← 【13 大核心执行引擎模块】
│   ├── narrative_engine.py        ← 模块1: Pass 1 剧力事件骨架生成与断言器
│   ├── style_compiler.py          ← 模块2: 一键文风特征挖掘与编译器
│   ├── prompt_builder.py          ← 模块3: Few-Shot 原著切片与四场次提示词编译
│   ├── novel_linter.py            ← 模块4: Universal Fiction Linter 代码级质检器
│   ├── auto_healer.py             ← 模块5: 违规文本自愈修复器 (定向物理化，满分自愈)
│   ├── longitudinal_linter.py     ← 模块6: 跨章节‘反土拨鼠之日’纵向向量审查器
│   ├── world_state_ledger.py      ← 模块7: 长程因果与世界线状态账本 (防吃书)
│   ├── scene_expander.py          ← 模块8: 四场次物理渐进生成与拼接引擎 (锁定3000字)
│   ├── macro_tension_analyzer.py  ← 模块9: 名作整卷张力潮汐逆向解构器 (ASCII心电图)
│   ├── grill_engine.py            ← 模块10: 总编级 Grill-Me 地基质询器 (6大承重柱)
│   ├── plot_tracker.py            ← 模块11: 跨章节伏笔与时间锁追踪器
│   ├── branching_generator.py     ← 模块12: 剧情十字路口 A/B/C 三走向推演
│   └── novel_pipeline.py          ← 双层流水线总调度集成入口
│
├── 📂 profiles/                    ← 【预编译名家文风画像库】(JSON + MD)
│   ├── 微微一笑很倾城_顾漫.json / .md
│   ├── 道诡异仙_狐尾的笔.json / .md
│   └── 大奉打更人_卖报小郎君.json / .md
│
├── 📂 corpus/                      ← 【参考名作语料池】
├── 📂 rules/                       ← 【系统级门禁约束】(AGENTS.md)
├── 📂 templates/                   ← 【Obsidian 创作卡片模板】(设定/人物/卷/分卷)
└── 📂 docs/                        ← 【工程化规范与全流程白皮书】
    ├── 7阶创作全生命周期深度闭环白皮书.md
    └── 通用小说工程化工具架构规范.md
```

---

## 🚀 极速上手与使用方法

### 方式 1：双击便携菜单（创作者图形控制台）
直接双击根目录下的 `启动助手.bat`，即可呼出 13 选 1 控制台：
- **`[1]` 编译新语料文风**：拖入任意全本 TXT，秒级提炼对话比、突发度、修辞密度与专属手艺；
- **`[2]` 伏笔到期排查**：输入章节号，自动核验本章应回收的暗线与时间锁；
- **`[3]` 卡文分支推演**：输入情境，生成 A（强冲突）、B（心理利益暗流）、C（认知反转）三种走向；
- **`[4]` 运行 Universal Linter**：代码级体检草稿，精准拦截假大空与滥调；
- **`[5]` 查阅白皮书**：查阅 7 阶创作全生命周期规范与黄金分场律；
- **`[6]` Grill-Me 质询**：针对 6 大核心承重柱开展总编级对齐访谈，筑牢新书地基；
- **`[7]` 编译名家 Few-Shot**：提取原著高光入局切片与四场次 3,000 字预算提示词；
- **`[8]` 跨章反土拨鼠体检**：计算首尾段向量余弦相似度与时空拓扑连续度，杜绝千篇一律；
- **`[9]` Pass 1 剧力骨架断言**：规划四场次分镜并强制断言大事件、戏剧阻力与硬切点；
- **`[10]` Auto-Healer 自愈修复**：将有瑕疵的草稿一键修复至 100 分纯净正文；
- **`[11]` 名作整卷张力潮汐**：逆向解构参考名作前 20~30 章张力潮汐心电图；
- **`[12]` 因果状态机简报**：排查主角负伤倒计时、随身银两与 NPC 疑心矩阵（防吃书）；
- **`[13]` 挂载至全生态终端**：一键将技能与规则自动分发到 CC / DSH / Codex / Antigravity。

### 方式 2：作为 MCP Server 接入（Claude Code / Cursor / DSH）
本插件内置纯 Python 标准库实现的 `mcp_server.py`，支持直接挂载为 MCP 工具服务：
```bash
# 启动 MCP 服务 (支持 stdio JSON-RPC 2.0)
python mcp_server.py
```
在 Claude Code 中一键添加：
```bash
claude mcp add novel-crafting python "E:/odsidian/gemini/小说创作/_工具/NovelCrafting-Plugin/mcp_server.py"
```

---

## 🛡️ 工业级去 AI 味质检标准矩阵 (Universal Fiction Linter)

| 质检维度 | 规则硬门禁 | 自动化惩罚 / 处置手段 |
| :--- | :--- | :--- |
| **抽象情绪泛滥** | 严禁“钻心的痛/心中一紧/倒吸凉气/瞳孔骤缩” | 扣 15 分/处，Auto-Healer 强制替换为具体生理动作与神经反射 |
| **人生导师鸡汤升华** | 100% 绝对封杀段末/章末说教（“这就是人生/只要...就总有...”） | 扣 25 分/处，Auto-Healer 强制硬切在器物、对白或动作上 |
| **修辞比喻密度** | 每千字比喻数强制 $\le 2.5$ 个，严禁机械无增量套话 | 超标即报警，拦截“生锈冰锥/大山/断线风筝”等滥俗隐喻 |
| **景物注水率** | 纯景物描写句占比严格控制在 $\le 15\%$ | 超标扣 15 分，镜头必须死死锁定人物动态交互与微观动作链 |
| **句式突发度 (Burstiness)** | 衡量句长方差，突发度必须 $\ge 0.60$ | 杜绝匀速散文叙事，强制使用短句、单字行与打断式对白切分 |
| **单章篇幅刚性配额** | 单章黄金区间 **2,800 ~ 4,000 字** | Scene Expander 逐场次渐进缝合，杜绝 1,200 字仓促大纲 |
