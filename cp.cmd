@echo off
chcp 65001 >nul
REM Capability Manager - 能力管理器快捷指令
REM 用法: cp write_report "主題"

pushd "%~dp0"
python .claude/capability-manager/cp.py %*
popd
