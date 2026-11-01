# -*- coding: utf-8 -*-
"""
Novel-Crafting 跨生态一键全能分发安装脚本 (Universal Multi-Agent Plugin Installer)
支持自动检测并一键挂载至：
1. Claude Code (cc)           -> ~/.claude/skills/novel-crafting/ + CLAUDE.md
2. DeepSeek Harness (dsh)     -> ~/.agents/skills/novel-crafting/ + package.json
3. OpenAI Codex (codex)       -> AGENTS.md + MCP Server
4. Google Antigravity (agy)   -> ~/.gemini/config/plugins/novel-crafting/
5. Cursor / Windsurf IDE      -> .cursorrules
"""

import sys
import io
import os
import shutil
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

USER_HOME = os.path.expanduser("~")
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

print("==========================================================")
print(" 🚀 Novel-Crafting 跨平台 AI Agent 全能插件安装器")
print("    适配: Codex / DeepSeek Harness (dsh) / Claude Code (cc)")
print("==========================================================")
print(f"📦 插件源目录: {SOURCE_DIR}")
print(f"🏠 用户主目录: {USER_HOME}\n")

installed_targets = []

def safe_copy_tree(src, dst):
    """Safely copy directory tree avoiding __pycache__ lock issues and merging smoothly."""
    os.makedirs(dst, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

# -------------------------------------------------------------
# 1. 安装至 Claude Code (cc)
# -------------------------------------------------------------
claude_dir = os.path.join(USER_HOME, ".claude")
claude_skills_dir = os.path.join(claude_dir, "skills", "novel-crafting")
try:
    os.makedirs(claude_skills_dir, exist_ok=True)
    # 拷贝核心必要组件
    shutil.copy2(os.path.join(SOURCE_DIR, "SKILL.md"), os.path.join(claude_skills_dir, "SKILL.md"))
    shutil.copy2(os.path.join(SOURCE_DIR, "CLAUDE.md"), os.path.join(claude_skills_dir, "CLAUDE.md"))
    
    # 复制 core 与 profiles
    safe_copy_tree(os.path.join(SOURCE_DIR, "core"), os.path.join(claude_skills_dir, "core"))
    safe_copy_tree(os.path.join(SOURCE_DIR, "profiles"), os.path.join(claude_skills_dir, "profiles"))

    # 拷贝 MCP 服务器脚本
    shutil.copy2(os.path.join(SOURCE_DIR, "mcp_server.py"), os.path.join(claude_skills_dir, "mcp_server.py"))

    # 配置全局 mcp.json (如果存在或生成)
    mcp_config_path = os.path.join(claude_dir, "mcp.json")
    mcp_data = {"mcpServers": {}}
    if os.path.exists(mcp_config_path):
        try:
            with open(mcp_config_path, "r", encoding="utf-8") as f:
                mcp_data = json.load(f)
        except Exception:
            pass
    if "mcpServers" not in mcp_data:
        mcp_data["mcpServers"] = {}
    mcp_data["mcpServers"]["novel-crafting"] = {
        "command": "python",
        "args": [os.path.join(claude_skills_dir, "mcp_server.py")]
    }
    with open(mcp_config_path, "w", encoding="utf-8") as f:
        json.dump(mcp_data, f, ensure_ascii=False, indent=2)

    installed_targets.append("Claude Code (cc) 全局技能与 MCP Server (~/.claude/skills/novel-crafting/)")
    print("✅ [1/5] Claude Code (cc) 安装成功！")
except Exception as e:
    print(f"⚠️ [1/5] Claude Code (cc) 配置提示: {e}")

# -------------------------------------------------------------
# 2. 安装至 DeepSeek Harness (dsh)
# -------------------------------------------------------------
dsh_agents_dir = os.path.join(USER_HOME, ".agents")
dsh_skills_dir = os.path.join(dsh_agents_dir, "skills", "novel-crafting")
try:
    os.makedirs(dsh_skills_dir, exist_ok=True)
    shutil.copy2(os.path.join(SOURCE_DIR, "SKILL.md"), os.path.join(dsh_skills_dir, "SKILL.md"))
    shutil.copy2(os.path.join(SOURCE_DIR, "package.json"), os.path.join(dsh_skills_dir, "package.json"))
    shutil.copy2(os.path.join(SOURCE_DIR, "AGENTS.md"), os.path.join(dsh_skills_dir, "AGENTS.md"))
    shutil.copy2(os.path.join(SOURCE_DIR, "mcp_server.py"), os.path.join(dsh_skills_dir, "mcp_server.py"))

    safe_copy_tree(os.path.join(SOURCE_DIR, "core"), os.path.join(dsh_skills_dir, "core"))
    safe_copy_tree(os.path.join(SOURCE_DIR, "profiles"), os.path.join(dsh_skills_dir, "profiles"))

    installed_targets.append("DeepSeek Harness (dsh) 官方技能目录 (~/.agents/skills/novel-crafting/)")
    print("✅ [2/5] DeepSeek Harness (dsh) 安装成功！")
except Exception as e:
    print(f"⚠️ [2/5] DeepSeek Harness (dsh) 配置提示: {e}")

# -------------------------------------------------------------
# 3. 安装至 OpenAI Codex / 通用 Coding Agent 环境
# -------------------------------------------------------------
codex_dir = os.path.join(USER_HOME, ".codex")
try:
    os.makedirs(codex_dir, exist_ok=True)
    shutil.copy2(os.path.join(SOURCE_DIR, "AGENTS.md"), os.path.join(codex_dir, "AGENTS.md"))
    shutil.copy2(os.path.join(SOURCE_DIR, "SKILL.md"), os.path.join(codex_dir, "SKILL.md"))
    installed_targets.append("OpenAI Codex 全局规则与技能 (~/.codex/AGENTS.md)")
    print("✅ [3/5] OpenAI Codex / 通用 Agent 安装成功！")
except Exception as e:
    print(f"⚠️ [3/5] OpenAI Codex 配置提示: {e}")

# -------------------------------------------------------------
# 4. 安装至 Google Antigravity / Gemini CLI (agy)
# -------------------------------------------------------------
agy_plugin_dir = os.path.join(USER_HOME, ".gemini", "config", "plugins", "novel-crafting")
try:
    os.makedirs(agy_plugin_dir, exist_ok=True)
    shutil.copy2(os.path.join(SOURCE_DIR, "plugin.json"), os.path.join(agy_plugin_dir, "plugin.json"))
    shutil.copy2(os.path.join(SOURCE_DIR, "README.md"), os.path.join(agy_plugin_dir, "README.md"))
    
    # rules
    agy_rules_dir = os.path.join(agy_plugin_dir, "rules")
    os.makedirs(agy_rules_dir, exist_ok=True)
    shutil.copy2(os.path.join(SOURCE_DIR, "AGENTS.md"), os.path.join(agy_rules_dir, "AGENTS.md"))

    # skills
    agy_skills_dir = os.path.join(agy_plugin_dir, "skills", "novel-crafting")
    os.makedirs(agy_skills_dir, exist_ok=True)
    shutil.copy2(os.path.join(SOURCE_DIR, "SKILL.md"), os.path.join(agy_skills_dir, "SKILL.md"))

    # core & scripts
    safe_copy_tree(os.path.join(SOURCE_DIR, "core"), os.path.join(agy_plugin_dir, "core"))
    safe_copy_tree(os.path.join(SOURCE_DIR, "core"), os.path.join(agy_plugin_dir, "skills", "novel-crafting", "scripts"))

    # profiles
    safe_copy_tree(os.path.join(SOURCE_DIR, "profiles"), os.path.join(agy_plugin_dir, "profiles"))
    safe_copy_tree(os.path.join(SOURCE_DIR, "profiles"), os.path.join(agy_plugin_dir, "skills", "novel-crafting", "profiles"))

    # mcp_server
    shutil.copy2(os.path.join(SOURCE_DIR, "mcp_server.py"), os.path.join(agy_plugin_dir, "mcp_server.py"))

    installed_targets.append("Google Antigravity 全局插件目录 (~/.gemini/config/plugins/novel-crafting/)")
    print("✅ [4/5] Google Antigravity (agy) 安装成功！")
except Exception as e:
    print(f"⚠️ [4/5] Google Antigravity 配置提示: {e}")

# -------------------------------------------------------------
# 5. 生成当前工程/知识库的本地规则 (.cursorrules & CLAUDE.md)
# -------------------------------------------------------------
try:
    workspace_dir = os.path.dirname(os.path.dirname(SOURCE_DIR)) # 如 E:\odsidian\gemini\小说创作
    for rule_file in [".cursorrules", "CLAUDE.md", "AGENTS.md"]:
        src_f = os.path.join(SOURCE_DIR, rule_file)
        dst_f = os.path.join(workspace_dir, rule_file)
        if os.path.exists(src_f) and src_f != dst_f:
            shutil.copy2(src_f, dst_f)
    installed_targets.append(f"本地知识库根目录规则 ({workspace_dir})")
    print("✅ [5/5] 本地知识库工作区 rules 部署成功！")
except Exception as e:
    print(f"⚠️ [5/5] 本地工程部署提示: {e}")

print("\n" + "=" * 65)
print("🎉 恭喜！Novel-Crafting 跨平台多 Agent 插件已全部完成部署！")
print("==========================================================")
for idx, item in enumerate(installed_targets, 1):
    print(f"  [{idx}] {item}")
print("==========================================================")
print("💡 使用方式速览:")
print("  - 在 Claude Code (cc) 中:  直接在任何项目输入 /novel-crafting 或对话小说创作")
print("  - 在 DeepSeek Harness (dsh) 中: 自动识别 ~/.agents/skills/novel-crafting/")
print("  - 在 OpenAI Codex 中:       通过 AGENTS.md 规范自动约束 Two-Pass 流水线")
print("  - 在 Cursor / Windsurf 中:  自动读取 .cursorrules 门禁")
print("  - 双击运行便携控制台:       运行 启动助手.bat")
print("==========================================================\n")
