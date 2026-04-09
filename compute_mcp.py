from typing import Annotated, Any
from mcp.server.auth.provider import TokenVerifier, AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp.tools import Tool
from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase
from nacos_mcp_wrapper.server.nacos_mcp import NacosMCP
from nacos_mcp_wrapper.server.nacos_settings import NacosSettings
from pydantic import Field, AnyHttpUrl

from phnix_nacos_mcp import PhnixNacosMCP


# ====================== Token 校验器 ======================
class MyTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        VALID_TOKENS = {
            "mcp-token-20260403-abcdef": "mcp-client",
            "mcp-token-dev-1234567890": "dev-client",
        }
        if token not in VALID_TOKENS:
            return None

        return AccessToken(
            token=token,
            client_id=VALID_TOKENS[token],
            scopes=["read", "write"],
        )


# ====================== 工具入参出参（必须继承 ArgModelBase）======================
class MyToolInput(ArgModelBase):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


class MyToolOutput(ArgModelBase):
    sum: int = Field(description="两个数字的和")
    product: int = Field(description="两个数字的积")


def calculate(input: MyToolInput) -> MyToolOutput:
    return MyToolOutput(
        sum=input.a + input.b,
        product=input.a * input.b
    )


# ====================== Nacos 配置 ======================
nacos_settings = NacosSettings()
nacos_settings.SERVER_ADDR = "47.245.135.32:8848"
nacos_settings.NAMESPACE = "mcp-dev"
nacos_settings.USERNAME = "service@mcp"
nacos_settings.PASSWORD = "nacos20260407"

# ====================== 认证配置 ======================
auth_settings = AuthSettings(
    issuer_url=AnyHttpUrl("http://localhost:18001"),
    resource_server_url=AnyHttpUrl("http://localhost:18001"),
)

# ====================== ✅ 完全正确的 Tool 写法 ======================
mcp = PhnixNacosMCP(
    name="compute-mcp",
    instructions="计算 MCP 服务",
    nacos_settings=nacos_settings,
    version="1.0.5",
    port=18001,
    auth=auth_settings,
    token_verifier=MyTokenVerifier(),
    tools=[
        Tool.from_function(
            fn=calculate,
            name="calculate",
            title="数字计算工具",
            description="输入两个数字，返回和与积",
        )
    ]
)


# ====================== 工具函数 ======================
@mcp.tool(description="计算两个整数相加的结果")
def add(
        a: Annotated[int, Field(description="被加数")],
        b: Annotated[int, Field(description="加数")]
) -> int:
    return a + b


@mcp.tool(description="计算两个整数相减的结果")
def minus(
        a: Annotated[int, Field(description="被减数")],
        b: Annotated[int, Field(description="减数")]
) -> int:
    return a - b


# ====================== 启动 ======================
if __name__ == "__main__":
    print("✅ MCP 服务启动（Token认证 + tools列表 + 自动注销）")
    mcp.run(transport="sse")
