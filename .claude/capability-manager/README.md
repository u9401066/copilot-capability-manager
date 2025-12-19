# 能力管理器 (Capability Manager)

此目錄包含 Copilot 能力管理系統的定義檔案。

## 目錄結構

```
.claude/
├── skills/              # 個別技能定義
│   ├── web-search/
│   ├── report-generator/
│   └── ...
├── workflows/           # 工作流程組合
│   ├── write_report.yaml
│   ├── project_check.yaml
│   └── ...
└── capability-manager/  # 能力管理器
    ├── README.md
    ├── registry.yaml    # 技能註冊表
    └── active.yaml      # 當前啟用的工作流程
```

## 使用方式

在 Copilot Chat 中使用：

```
/cp.write_report [主題]
/cp.project_check
/cp.deploy
```

## 工作流程

每個工作流程由多個 Skills 組成，按順序執行。
