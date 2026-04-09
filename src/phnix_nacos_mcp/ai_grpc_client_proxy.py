import base64
import hashlib
import hmac
import logging
import uuid
from typing import Optional

from a2a.types import AgentCard

from v2.nacos import ClientConfig, NacosException
from v2.nacos.ai.model.a2a.a2a import AgentCardDetailInfo, AgentEndpoint
from v2.nacos.ai.model.ai_constant import AIConstants
from v2.nacos.ai.model.ai_request import AbstractAIRequest, AbstractMcpRequest, \
    QueryMcpServerRequest, ReleaseMcpServerRequest, McpServerEndpointRequest, \
    QueryAgentCardRequest, ReleaseAgentCardRequest, AgentEndpointRequest
from v2.nacos.ai.model.ai_response import QueryMcpServerResponse, \
    ReleaseMcpServerResponse, McpServerEndpointResponse, QueryAgentCardResponse, \
    ReleaseAgentCardResponse, AgentEndpointResponse
from v2.nacos.ai.model.cache.agent_info_cache import AgentInfoCacheHolder
from v2.nacos.ai.model.cache.mcp_server_info_cache import \
    McpServerInfoCacheHolder
from v2.nacos.ai.model.mcp.mcp import McpServerBasicInfo, McpToolSpecification, \
    McpEndpointSpec, McpServerDetailInfo
from v2.nacos.ai.redo.ai_grpc_redo_service import AIGrpcRedoService
from v2.nacos.ai.remote.ai_grpc_client_proxy import AIGRPCClientProxy
from v2.nacos.common.constants import Constants
from v2.nacos.common.nacos_exception import SERVER_ERROR, SERVER_NOT_IMPLEMENTED
from v2.nacos.transport.ability import AbilityKey, AbilityStatus
from v2.nacos.transport.http_agent import HttpAgent
from v2.nacos.transport.nacos_server_connector import NacosServerConnector
from v2.nacos.transport.rpc_client import ConnectionType
from v2.nacos.transport.rpc_client_factory import RpcClientFactory
from v2.nacos.utils.common_util import get_current_time_millis
from v2.nacos.utils.md5_util import md5

from phnix_nacos_mcp.mcp_server_info_cache import PhnixMcpServerInfoCacheHolder
from phnix_nacos_mcp.model.mcp_param import PhnixMcpToolSpecification, PhnixReleaseMcpServerRequest, \
    PhnixMcpServerDetailInfo
from phnix_nacos_mcp.model.mcp_response import PhnixQueryMcpServerResponse


class PhnixAIGRPCClientProxy(AIGRPCClientProxy):

    def __init__(self,
                 client_config: ClientConfig,
                 http_client: HttpAgent):
        super().__init__(client_config, http_client)
        self.cache_holder: Optional[PhnixMcpServerInfoCacheHolder] = None

    async def query_mcp_server(self, mcp_name: str, version: str) -> PhnixMcpServerDetailInfo:
        if not self.is_ability_supported_by_server(AbilityKey.SERVER_MCP_REGISTRY):
            raise NacosException(SERVER_NOT_IMPLEMENTED,
                                 "Request Nacos server version is too low, not support mcp registry feature.")

        request = QueryMcpServerRequest(
            namespaceId=self.namespace_id,
            mcpName=mcp_name,
            version=version,
        )

        response = await self.request_ai_server(request, QueryMcpServerResponse)
        mcpServerDetailInfo: McpServerDetailInfo = response.mcpServerDetailInfo
        return PhnixMcpServerDetailInfo(**mcpServerDetailInfo.model_dump())

    async def release_mcp_server(self, server_spec: McpServerBasicInfo, tool_spec: PhnixMcpToolSpecification,
                                 endpoint_spec: McpEndpointSpec):
        self.logger.info(
            f"[{self.uuid}] release mcp server: {server_spec.name}, version {server_spec.versionDetail.version}")
        if not self.is_ability_supported_by_server(AbilityKey.SERVER_MCP_REGISTRY):
            raise NacosException(SERVER_NOT_IMPLEMENTED,
                                 "Request Nacos server version is too low, not support mcp registry feature.")

        request = PhnixReleaseMcpServerRequest(
            namespaceId=self.namespace_id,
            mcpName=server_spec.name,
            serverSpecification=server_spec,
            toolSpecification=tool_spec,
            endpointSpecification=endpoint_spec
        )

        response = await self.request_ai_server(request, ReleaseMcpServerResponse)
        return response.mcpId

    async def subscribe_mcp_server(self, mcp_name: str, version: str) -> PhnixMcpServerDetailInfo:
        if not self.is_ability_supported_by_server(AbilityKey.SERVER_MCP_REGISTRY):
            raise NacosException(SERVER_NOT_IMPLEMENTED,
                                 "Request Nacos server version is too low, not support mcp registry feature.")

        mcp_detail_info = await self.cache_holder.get_mcp_server(mcp_name, version)
        if mcp_detail_info is None:
            mcp_detail_info = await self.query_mcp_server(mcp_name, version)
            await self.cache_holder.process_mcp_server_detail_info(mcp_detail_info)
            await self.cache_holder.add_mcp_server_update_task(mcp_name, version)

        return mcp_detail_info
