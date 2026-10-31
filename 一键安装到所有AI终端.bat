@echo off
chcp 65001 >nul
title Novel-Crafting 跨生态全能插件安装器

echo ========================================================
echo   正在自动部署 Novel-Crafting 插件至全平台 AI 终端...
echo   (Claude Code / DeepSeek Harness / Codex / Antigravity / Cursor)
echo ========================================================

python "%~dp0install_universal.py"

echo.
pause
