"""
MCP Server Entry Point
MCP 伺服器入口點

使用方式：
    python -m src.capability_engine.infrastructure.mcp.server
    
或透過 mcp.json 設定讓 VS Code 自動啟動
"""

import asyncio
import sys
from pathlib import Path

# 確保可以找到模組
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from src.capability_engine.infrastructure.mcp.server import run_mcp_server

if __name__ == "__main__":
    asyncio.run(run_mcp_server())
