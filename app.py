import asyncio
import logging
import os

from v2.nacos import ClientConfigBuilder, NacosException
from v2.nacos.ai.model.mcp.mcp import McpServerBasicInfo, McpServerRemoteServiceConfig
from v2.nacos.ai.model.mcp.registry import ServerVersionDetail
from v2.nacos.ai.nacos_ai_service import NacosAIService
from v2.nacos.ai.model.ai_param import (
    GetMcpServerParam,
    ReleaseMcpServerParam,
    RegisterMcpServerEndpointParam,
    SubscribeMcpServerParam
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 【全局强制代理：所有请求都走 Reqable】
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:9000'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:9000'
os.environ['NO_PROXY'] = ''  # 清空，不走直连，全部走代理

# Nacos 客户端配置
client_config = (ClientConfigBuilder()
                 .server_address("47.245.135.32:8848")
                 .username("nacos")
                 .password("nacos")
                 .namespace_id("mcp-dev")
                 .build())

MCP_NAME = "compute-mcp"
MCP_VERSION = "1.0.6"


async def main():
    """主异步函数"""
    ai_client = None
    try:
        # 创建 AI 服务客户端
        logger.info("正在创建 Nacos AI 服务客户端...")
        ai_client = await NacosAIService.create_ai_service(client_config)
        logger.info("Nacos AI 服务客户端创建成功")

        # 获取 MCP 服务器
        try:
            logger.info(f"正在获取 MCP 服务器: {MCP_NAME}, 版本: {MCP_VERSION}")
            mcp_server = await ai_client.get_mcp_server(
                GetMcpServerParam(mcp_name=MCP_NAME, version=MCP_VERSION)
            )
            logger.info(f"获取 MCP 服务器成功: {mcp_server}")
        except NacosException as e:
            logger.error(f"MCP服务未找到：{e.message}")

            # 发布 MCP 服务器
            logger.info(f"正在发布 MCP 服务器: {MCP_NAME}")
            server_spec = McpServerBasicInfo(
                name=MCP_NAME,
                description='My MCP Server',
                protocol='http',
                frontProtocol='mcp-sse',
                remoteServerConfig=McpServerRemoteServiceConfig(exportPath='/sse'),
                versionDetail=ServerVersionDetail(version=MCP_VERSION, is_latest=True)
            )
            result = await ai_client.release_mcp_server(
                ReleaseMcpServerParam(server_spec=server_spec)
            )
            logger.info(f"发布 MCP 服务器成功: {result}")

        # 注册 MCP 服务器端点
        logger.info(f"正在注册 MCP 服务器端点: 127.0.0.1:8080")
        await ai_client.register_mcp_server_endpoint(
            RegisterMcpServerEndpointParam(
                mcp_name=MCP_NAME,
                address='127.0.0.1',
                port=8080,
                version=MCP_VERSION
            )
        )
        logger.info("注册 MCP 服务器端点成功")

        # 订阅 MCP 服务器
        async def mcp_listener(mcp_id, namespace_id, mcp_name, mcp_server_detail):
            logger.info(f"MCP Server 变更: {mcp_name}, 版本: {mcp_server_detail.version}")

        logger.info(f"正在订阅 MCP 服务器: {MCP_NAME}")
        await ai_client.subscribe_mcp_server(
            SubscribeMcpServerParam(
                mcp_name=MCP_NAME,
                version=MCP_VERSION,
                subscribe_callback=mcp_listener
            )
        )
        logger.info("订阅 MCP 服务器成功")

        # 保持运行以接收订阅通知
        logger.info("服务正在运行，按 Ctrl+C 停止...")
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"发生错误: {e}", exc_info=True)
        raise
    finally:
        if ai_client:
            logger.info("正在关闭客户端...")
            # 如果有关闭方法，可以在这里调用
            # await ai_client.close()


if __name__ == '__main__':
    asyncio.run(main())
