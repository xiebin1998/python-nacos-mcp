from v2.nacos import NacosException, ClientConfig
from v2.nacos.ai.model.ai_constant import AIConstants
from v2.nacos.ai.model.ai_param import GetMcpServerParam, SubscribeMcpServerParam
from v2.nacos.ai.nacos_ai_service import NacosAIService
from v2.nacos.common.nacos_exception import INVALID_PARAM

from phnix_nacos_mcp.ai_grpc_client_proxy import PhnixAIGRPCClientProxy
from phnix_nacos_mcp.mcp_server_info_cache import PhnixMcpServerInfoCacheHolder
from phnix_nacos_mcp.mcp_server_subscribe_manager import PhnixMcpServerSubscribeManager
from phnix_nacos_mcp.model.mcp_param import PhnixReleaseMcpServerParam, PhnixMcpServerDetailInfo, \
    PhnixSubscribeMcpServerParam


class PhnixNacosAIService(NacosAIService):

    def __init__(self, client_config: ClientConfig):
        super().__init__(client_config)
        self.grpc_client_proxy = PhnixAIGRPCClientProxy(client_config, self.http_agent)
        self.mcp_server_subscribe_manager = PhnixMcpServerSubscribeManager()

        self.grpc_client_proxy = PhnixAIGRPCClientProxy(client_config, self.http_agent)
        self.mcp_server_cache_holder = PhnixMcpServerInfoCacheHolder(
            self.mcp_server_subscribe_manager, self.grpc_client_proxy)

    @staticmethod
    async def create_ai_service(client_config: ClientConfig) -> 'PhnixNacosAIService':
        ai_service = PhnixNacosAIService(client_config)
        await ai_service.start()
        return ai_service

    async def start(self):
        await self.grpc_client_proxy.start(self.mcp_server_cache_holder, self.agent_info_cache_holder)
        pass

    async def get_mcp_server(self, param: GetMcpServerParam) -> PhnixMcpServerDetailInfo:
        if not param.mcp_name or len(param.mcp_name) == 0:
            raise NacosException(INVALID_PARAM, "mcpName is required")

        return await self.grpc_client_proxy.query_mcp_server(param.mcp_name, param.version)

    pass

    async def release_mcp_server(self, param: PhnixReleaseMcpServerParam) -> str:
        if not param.server_spec:
            raise NacosException(INVALID_PARAM, "serverSpec is required")
        if not param.server_spec.name or len(param.server_spec.name) == 0:
            raise NacosException(INVALID_PARAM, "serverSpec.name is required")
        if not param.server_spec.versionDetail.version or len(param.server_spec.versionDetail.version) == 0:
            raise NacosException(INVALID_PARAM, "serverSpec.versionDetail.version is required")

        if not param.mcp_endpoint_spec is None and param.mcp_endpoint_spec.type == AIConstants.MCP_ENDPOINT_TYPE_REF:
            if "namespaceId" not in param.mcp_endpoint_spec.data:
                param.mcp_endpoint_spec.data["namespaceId"] = self.namespace_id
            elif param.mcp_endpoint_spec.data["namespaceId"] != self.namespace_id:
                raise NacosException(INVALID_PARAM, "mcpEndpointSpec.data.namespaceId is not match")

        return await self.grpc_client_proxy.release_mcp_server(param.server_spec, param.tool_spec,
                                                               param.mcp_endpoint_spec)

    async def subscribe_mcp_server(self, param: PhnixSubscribeMcpServerParam) -> PhnixMcpServerDetailInfo:
        if not param.mcp_name or len(param.mcp_name) == 0:
            raise NacosException(INVALID_PARAM, "mcpName is required")

        if not param.subscribe_callback:
            raise NacosException(INVALID_PARAM, "subscribeCallback is required")

        await self.mcp_server_subscribe_manager.register_subscriber(param.mcp_name, param.version,
                                                                    param.subscribe_callback)
        result = await self.grpc_client_proxy.subscribe_mcp_server(param.mcp_name, param.version)
        return result
