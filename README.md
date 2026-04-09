# Phnix Nacos MCP

一个用于 Nacos MCP 服务器注册和管理的 Python 包装器库。

## 功能特性

- 支持将 MCP 服务器注册到 Nacos 服务发现平台
- 支持多种传输协议：stdio、SSE、StreamableHTTP
- 自动服务发现和注册
- 兼容 Nacos MCP 生态系统

## 安装

```bash
pip install phnix-nacos-mcp
```

## 快速开始

### 基本使用

```python
from phnix_nacos_mcp import PhnixNacosMCP
from nacos_mcp_wrapper.server.nacos_settings import NacosSettings

# 配置 Nacos 设置
nacos_settings = NacosSettings(
    SERVER_ADDR="localhost:8848",
    NAMESPACE="public",
    USERNAME="nacos",
    PASSWORD="nacos"
)

# 创建 MCP 服务器实例
mcp = PhnixNacosMCP(
    name="my-mcp-server",
    version="1.0.0",
    nacos_settings=nacos_settings,
    instructions="这是一个示例 MCP 服务器"
)

# 添加工具
@mcp.tool()
def my_tool(param: str) -> str:
    """示例工具"""
    return f"处理结果: {param}"

# 运行服务器
if __name__ == "__main__":
    mcp.run()
```

### 使用 stdio 传输

```python
import asyncio
from phnix_nacos_mcp import PhnixNacosMCP

mcp = PhnixNacosMCP(name="my-server", version="1.0.0")

asyncio.run(mcp.run_stdio_async())
```

### 使用 SSE 传输

```python
import asyncio
from phnix_nacos_mcp import PhnixNacosMCP

mcp = PhnixNacosMCP(
    name="my-server",
    version="1.0.0",
    host="0.0.0.0",
    port=8000
)

asyncio.run(mcp.run_sse_async())
```

### 使用 StreamableHTTP 传输

```python
import asyncio
from phnix_nacos_mcp import PhnixNacosMCP

mcp = PhnixNacosMCP(
    name="my-server",
    version="1.0.0",
    host="0.0.0.0",
    port=8000
)

asyncio.run(mcp.run_streamable_http_async())
```

## 配置说明

### NacosSettings 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| SERVER_ADDR | Nacos 服务器地址 | localhost:8848 |
| NAMESPACE | 命名空间 | public |
| USERNAME | 用户名 | - |
| PASSWORD | 密码 | - |
| ACCESS_KEY | 访问密钥 | - |
| SECRET_KEY | 密钥 | - |
| SERVICE_IP | 服务 IP | 自动获取 |
| SERVICE_PORT | 服务端口 | 8000 |
| SERVICE_GROUP | 服务分组 | DEFAULT_GROUP |
| SERVICE_EPHEMERAL | 是否临时实例 | True |
| SERVICE_REGISTER | 是否注册服务 | True |
| SERVICE_META_DATA | 服务元数据 | {} |

## 依赖项

- Python >= 3.10
- mcp >= 1.0.0
- nacos-mcp-wrapper-python >= 0.1.0
- jsonref >= 1.0.0

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src/
isort src/
```

### 类型检查

```bash
mypy src/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### 0.1.0 (2026-04-08)

- 初始版本
- 支持基本的 MCP 服务器注册功能
- 支持 stdio、SSE、StreamableHTTP 传输协议