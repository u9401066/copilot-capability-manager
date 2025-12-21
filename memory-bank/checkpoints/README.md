# Checkpoint 目錄

此目錄用於存放長任務的狀態檢查點。

## 檔案格式

```json
{
  "capability": "capability-id",
  "status": "in-progress | completed | failed",
  "startedAt": "ISO 8601 timestamp",
  "lastUpdated": "ISO 8601 timestamp",
  "progress": {
    "total": 20,
    "completed": 8,
    "percentage": 40
  },
  "currentItem": "current-item-id",
  "completedItems": ["item-1", "item-2", ...],
  "pendingItems": ["item-9", "item-10", ...],
  "notes": [],
  "errors": []
}
```

## 使用方式

1. 執行 Capability 時自動建立
2. 每完成一個項目更新
3. 中斷後可從斷點繼續
4. 完成後可選擇保留或刪除
