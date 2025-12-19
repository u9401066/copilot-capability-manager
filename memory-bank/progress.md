# Progress (Updated: 2025-12-20)

## Done

- 建立完整專案模板 (48 檔案)
- 發布到 GitHub: u9401066/template-is-all-you-need
- 啟用 Template Repository 功能
- 新增 8 個主題標籤
- **重構專案為 Copilot Capability Manager**
- 實現 VS Code Prompt Files 機制 (`/cp.xxx` 斜線指令)
- 建立 8 個完整的 Prompt Files:
  - cp.write_report (撰寫報告)
  - cp.project_check (專案檢查)
  - cp.deploy (部署專案)
  - cp.cleanup (清理專案)
  - cp.commit (Git 提交)
  - cp.new_skill (新增技能)
  - cp.new_workflow (新增工作流程)
  - cp.help (顯示說明)
- 簡化 AGENTS.md (移除動態更新機制)
- 建立機制說明文檔 `docs/PROMPT-FILES-MECHANISM.md`
- 清理測試檔案和失敗套件:
  - 刪除 copilot-commands-extension/
  - 刪除 speckit-test/
  - 刪除 .specify/
  - 刪除未使用的 registry.yaml, active.yaml
- 更新 README.md 反映新的專案定位

## Doing

- 準備 Git commit

## Next

- 測試 /cp.xxx 指令是否正常運作
- 考慮是否需要 CLI 工具 (目前 cp.py 可選)
