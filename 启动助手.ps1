<#
.SYNOPSIS
    NovelCrafting-Plugin 通用便携启动控制台 (Universal Portable Console)
    完全自适应相对路径，拷贝到任何电脑或 Obsidian 库中均可直接双击运行。
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "NovelCrafting-Plugin 创作助手"

$ScriptDir = $PSScriptRoot
$CoreDir = Join-Path $ScriptDir "core"
$ProfilesDir = Join-Path $ScriptDir "profiles"
$CorpusDir = Join-Path $ScriptDir "corpus"

function Show-Menu {
    Clear-Host
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "     ✍️  NovelCrafting-Plugin 通用小说创作插件控制台     " -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host " [1] 📚 编译新语料文风 Profile (一键数理挖掘，解耦任何 TXT)" -ForegroundColor White
    Write-Host " [2] 🧵 跨章节伏笔与时间锁追踪 (检查本章到期暗线，防吃书)" -ForegroundColor White
    Write-Host " [3] 🎲 剧情十字路口多分支推演 (提供 A/B/C 三种高张力走向)" -ForegroundColor White
    Write-Host " [4] 🛡️ 运行 Novel Linter 静态体检 (检测 AI 假大空、滥俗比喻与升华)" -ForegroundColor White
    Write-Host " [5] 📖 查阅 7 阶创作全流程白皮书 (完整方法论、黄金三段律与自检 SOP)" -ForegroundColor White
    Write-Host " [6] 🎯 启动 Grill-Me 创意孵化与地基质询器 (总编级追问，逐项对齐新书地基)" -ForegroundColor White
    Write-Host " [7] 🎬 一键编译名家 Few-Shot 写作指令 (注入原著开篇/对白切片与四场次预算)" -ForegroundColor White
    Write-Host " [8] 🛰️ 运行跨章节“反土拨鼠之日”纵向审查 (首尾段余弦相似度与时空拓扑)" -ForegroundColor White
    Write-Host " [9] 🎭 运行 Pass 1 剧力事件骨架断言器 (四场次物理预算与信息差校验)" -ForegroundColor White
    Write-Host " [10] 🩹 运行 Auto-Healer 文本自愈修复器 (定向物理化滥俗词，硬切断章自愈100分)" -ForegroundColor White
    Write-Host " [11] 🌊 逆向名作整卷“张力潮汐心电图” (解构前20章波浪式生命呼吸律动)" -ForegroundColor White
    Write-Host " [12] 📋 查看 World State Ledger 因果状态简报 (防吃书: 生理伤势/余银/NPC疑心度)" -ForegroundColor White
    Write-Host " [13] 🌐 一键挂载至全生态终端 (Claude Code / DSH / Codex / Antigravity / Cursor)" -ForegroundColor Green
    Write-Host " [14] 🩸 从已写正文提取因果增量 (State Diff) 并同步世界账本" -ForegroundColor White
    Write-Host " [15] 🎯 逐场次多轮执笔提示词生成 (防1200字压缩，锁定3000字)" -ForegroundColor White
    Write-Host " [0] 🚪 退出" -ForegroundColor Gray
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host -NoNewline "请选择操作 [0-15]: "
}

do {
    Show-Menu
    $choice = Read-Host

    switch ($choice) {
        "1" {
            Write-Host "`n请输入语料 TXT 的路径 (支持拖拽文件到窗口):" -ForegroundColor Yellow
            $txtPath = Read-Host
            $txtPath = $txtPath.Trim('"', "'")
            if ([string]::IsNullOrWhiteSpace($txtPath)) {
                # 寻找 corpus 目录下的第一个 txt
                $sampleTxt = Get-ChildItem -Path $CorpusDir -Filter "*.txt" -File | Select-Object -First 1
                if ($sampleTxt) {
                    $txtPath = $sampleTxt.FullName
                }
            }
            if (-not (Test-Path $txtPath)) {
                Write-Host "❌ 文件不存在: $txtPath" -ForegroundColor Red
            } else {
                python (Join-Path $CoreDir "style_compiler.py") --corpus "$txtPath" --out "$ProfilesDir"
            }
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "2" {
            Write-Host "`n请输入你当前正在撰写或准备撰写的章节号 (如 15、25):" -ForegroundColor Yellow
            $chap = Read-Host
            if ([string]::IsNullOrWhiteSpace($chap)) { $chap = "15" }
            python -c "import sys; sys.path.append(r'$CoreDir'); from plot_tracker import PlotTracker; t = PlotTracker(); t.get_due_reminders($chap)"
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "3" {
            Write-Host "`n请输入当前现场情境简述:" -ForegroundColor Yellow
            $ctx = Read-Host
            if ([string]::IsNullOrWhiteSpace($ctx)) { $ctx = "主角刚推开密室的石门，发现桌上放着一封染血的书信。" }
            Write-Host "请输入当前核心剧情诉求/矛盾:" -ForegroundColor Yellow
            $obj = Read-Host
            if ([string]::IsNullOrWhiteSpace($obj)) { $obj = "信里的内容到底该如何颠覆主角的既往认知？" }
            python -c "import sys; sys.path.append(r'$CoreDir'); from branching_generator import generate_branches; generate_branches('''$ctx''', '''$obj''')"
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "4" {
            Write-Host "`n请输入要体检的文本内容或草稿文件路径 (直接回车运行内置基准测试):" -ForegroundColor Yellow
            $target = Read-Host
            $target = $target.Trim('"', "'")
            if ([string]::IsNullOrWhiteSpace($target)) {
                python (Join-Path $CoreDir "novel_pipeline.py")
            } elseif (Test-Path $target) {
                python -c "import sys; sys.path.append(r'$CoreDir'); from novel_pipeline import NovelPipeline; p = NovelPipeline(); text = open(r'$target', encoding='utf-8').read(); p.print_critique_report(text, label='$target')"
            } else {
                python -c "import sys; sys.path.append(r'$CoreDir'); from novel_pipeline import NovelPipeline; p = NovelPipeline(); p.print_critique_report('''$target''', label='输入片段')"
            }
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "5" {
            $docPath = Join-Path $ScriptDir "docs\创作全流程指引白皮书.md"
            if (-not (Test-Path $docPath)) {
                $docPath = Join-Path (Split-Path $ScriptDir -Parent) "创作全流程指引白皮书.md"
            }
            Write-Host "`n==========================================================" -ForegroundColor Green
            Write-Host "   📖 中文长篇小说 7 阶深度闭环指引体系 (SOP)   " -ForegroundColor Yellow
            Write-Host "==========================================================" -ForegroundColor Green
            Write-Host "【阶段 0】选题对标与文风编译 (下载名作 -> style_compiler.py -> 提炼 Linter 门禁)" -ForegroundColor White
            Write-Host "【阶段 1】世界观与代价法则工程 (力量必须绑定不可逆代价 -> 社会阶级断层)" -ForegroundColor White
            Write-Host "【阶段 2】人物心智与生理应激建模 (心智缺陷 -> 阶级盲区 -> 生理应激动作库)" -ForegroundColor White
            Write-Host "【阶段 3】故事大纲与伏笔时间锁 (三幕节拍 -> 伏笔图谱注册 -> 到期倒计时)" -ForegroundColor White
            Write-Host "【阶段 4】章节细纲黄金三段律 (10% 生理承接 -> 40% 利益心计 -> 50% 爆发新冲突)" -ForegroundColor White
            Write-Host "【阶段 5】剧情十字路口多分支推演 (branching_generator.py -> A/B/C 三走向)" -ForegroundColor White
            Write-Host "【阶段 6】执笔生成与代码级 Linter 静态质检 (动态 Profile -> 杜绝 AI 假大空)" -ForegroundColor White
            Write-Host "【阶段 7】伏笔回收闭环与图谱回写 (标记 [RESOLVED] -> 仪表盘进度同步)" -ForegroundColor White
            Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "完整白皮书已存放在: $docPath" -ForegroundColor Cyan
            Write-Host "可在 Obsidian 中直接点击阅读: [[创作全流程指引白皮书]]" -ForegroundColor Yellow
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "6" {
            python (Join-Path $CoreDir "grill_engine.py")
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "7" {
            Write-Host "`n请输入要挂载的作家/作品名称 (如: 顾漫、道诡异仙、大奉打更人):" -ForegroundColor Yellow
            $author = Read-Host
            if ([string]::IsNullOrWhiteSpace($author)) { $author = "顾漫" }
            Write-Host "请输入当前本章核心情境简述 (如: 苗希希与孟西昂在游戏里初次组队打副本):" -ForegroundColor Yellow
            $scene = Read-Host
            if ([string]::IsNullOrWhiteSpace($scene)) { $scene = "男女主初次组队，在副本门口发生冲突与试探" }
            python -c "import sys; sys.path.append(r'$CoreDir'); from prompt_builder import build_style_prompt; print(build_style_prompt('$author', '$scene', 3200))"
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "8" {
            Write-Host "`n请输入章节草稿所在目录 (直接回车默认审查当前项目的章节草稿):" -ForegroundColor Yellow
            $dDir = Read-Host
            if ([string]::IsNullOrWhiteSpace($dDir)) {
                $dDir = Join-Path (Split-Path (Split-Path $ScriptDir -Parent) -Parent) "小说创作\慢慢仙途\章节草稿"
                if (-not (Test-Path $dDir)) {
                    $dDir = Join-Path (Split-Path (Split-Path $ScriptDir -Parent) -Parent) "小说创作\小说一\章节草稿"
                }
            }
            if (-not (Test-Path $dDir)) {
                Write-Host "❌ 目录不存在: $dDir" -ForegroundColor Red
            } else {
                python -c "import sys; sys.path.append(r'$CoreDir'); from longitudinal_linter import LongitudinalLinter; l = LongitudinalLinter(); l.load_chapters_from_dir(r'$dDir'); l.print_longitudinal_report()"
            }
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "9" {
            python (Join-Path $CoreDir "narrative_engine.py")
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "10" {
            Write-Host "`n请输入要自愈修复的草稿文本路径 (或直接输入一小段文本):" -ForegroundColor Yellow
            $hText = Read-Host
            if ([string]::IsNullOrWhiteSpace($hText)) {
                $sampleFile = Join-Path (Split-Path (Split-Path $ScriptDir -Parent) -Parent) "小说创作\慢慢仙途\章节草稿\第二章.md"
                if (Test-Path $sampleFile) { $hText = $sampleFile }
            }
            if (Test-Path $hText) {
                python -c "import sys; sys.path.append(r'$CoreDir'); from auto_healer import AutoHealer; h = AutoHealer(); raw = open(r'$hText', encoding='utf-8').read(); res = h.heal(raw); print(f'自愈前: {res[\"original_score\"]} 分 -> 自愈后: {res[\"final_score\"]} 分'); [print(' *', c) for c in res['changes_log']]; open(r'$hText', 'w', encoding='utf-8').write(res['healed_text']); print('✅ 已将自愈修复后的文本回写至文件!')"
            } else {
                python -c "import sys; sys.path.append(r'$CoreDir'); from auto_healer import AutoHealer; h = AutoHealer(); res = h.heal('''$hText'''); print(f'自愈前: {res[\"original_score\"]} 分 -> 自愈后: {res[\"final_score\"]} 分'); [print(' *', c) for c in res['changes_log']]; print('\n修复后正文:\n', res['healed_text'])"
            }
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "11" {
            Write-Host "`n请输入要逆向解构的名著 TXT 路径 (直接回车默认分析大奉打更人前20章):" -ForegroundColor Yellow
            $cPath = Read-Host
            python -c "import sys; sys.path.append(r'$CoreDir'); from macro_tension_analyzer import MacroTensionAnalyzer; a = MacroTensionAnalyzer(); a.print_tension_curve(r'$cPath' if r'$cPath' else None, max_chapters=20)"
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "12" {
            python -c "import sys; sys.path.append(r'$CoreDir'); from world_state_ledger import WorldStateLedger; l = WorldStateLedger(); print(l.generate_context_brief_for_pass1())"
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "13" {
            python (Join-Path $ScriptDir "install_universal.py")
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "14" {
            Write-Host "`n请输入章节号 (如 5):" -ForegroundColor Yellow
            $cNum = Read-Host
            Write-Host "`n请输入已写正文 TXT/MD 路径 (或直接输入片段):" -ForegroundColor Yellow
            $cText = Read-Host
            $cText = $cText.Trim('"', "'")
            if (Test-Path $cText) {
                $rawText = Get-Content $cText -Raw -Encoding UTF8
            } else {
                $rawText = $cText
            }
            python -c "import sys; sys.path.append(r'$CoreDir'); from state_diff_extractor import StateDiffExtractor; e = StateDiffExtractor(); diff = e.extract_diff_from_chapter(int('$cNum' if '$cNum' else 1), '''$rawText'''); print('📋 提取到的增量:'); [print(' *', a) for a in diff['suggested_actions']]; brief = e.apply_diff_to_ledger(diff); print('\n✅ 状态机账本已同步更新:\n', brief)"
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "15" {
            Write-Host "`n请选择当前要执笔的场次编号 [1-4]:" -ForegroundColor Yellow
            $sId = Read-Host
            Write-Host "`n请输入该场次的动作推进细化剧情:" -ForegroundColor Yellow
            $sPlan = Read-Host
            Write-Host "`n请输入挂载的作家文风 (如'狐尾的笔'/'刘慈欣'/'顾漫'/'马伯庸'):" -ForegroundColor Yellow
            $sStyle = Read-Host
            python -c "import sys; sys.path.append(r'$CoreDir'); from scene_expander import SceneExpander; e = SceneExpander(); print('\n' + e.get_turn_prompt(int('$sId' if '$sId' else 1), '''$sPlan''', author_style='$sStyle'))"
            Write-Host "`n按回车键继续..." -ForegroundColor Gray; Read-Host | Out-Null
        }
        "0" {
            Write-Host "退出助手。祝创作顺利！" -ForegroundColor Cyan
            break
        }
    }
} while ($true)
