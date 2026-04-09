from typing import Optional, Dict, Any, List, Callable, Awaitable

from v2.nacos.ai.model.ai_param import ReleaseMcpServerParam, SubscribeMcpServerParam
from v2.nacos.ai.model.ai_request import ReleaseMcpServerRequest
from v2.nacos.ai.model.mcp.mcp import McpTool, McpServerBasicInfo, McpToolSpecification, McpEndpointSpec, \
    SecuritySchema, McpToolMeta, EncryptObject, McpEndpointInfo, McpServerDetailInfo
from v2.nacos.ai.model.mcp.registry import ServerVersionDetail


class PhnixMcpTool(McpTool):
    """Definition of a tool provided by MCP server"""
    # Name of the tool
    name: Optional[str] = None
    # Description of what the tool does
    description: Optional[str] = None
    # JSON schema defining the input parameters for the tool
    inputSchema: Optional[Dict[str, Any]] = None
    # JSON schema defining the output parameters for the tool
    outputSchema: Optional[Dict[str, Any]] = None


class PhnixMcpToolSpecification(McpToolSpecification):
    """Complete specification of tools provided by MCP server"""
    specificationType: Optional[str] = None
    encryptData: Optional[EncryptObject] = None
    # List of tools available on the MCP server
    tools: Optional[List[PhnixMcpTool]] = None
    # Metadata for each tool, keyed by tool name
    toolsMeta: Optional[Dict[str, McpToolMeta]] = None
    # Security schemas required for tool access
    securitySchema: Optional[List[SecuritySchema]] = None


class PhnixReleaseMcpServerParam(ReleaseMcpServerParam):
    """Parameter model for releasing/publishing MCP server"""
    # Basic information specification for the MCP server
    server_spec: Optional[McpServerBasicInfo] = None
    # Tool specification defining the tools provided by MCP server
    tool_spec: Optional[PhnixMcpToolSpecification] = None
    # Endpoint specification for MCP server network configuration
    mcp_endpoint_spec: Optional[McpEndpointSpec] = None


class PhnixReleaseMcpServerRequest(ReleaseMcpServerRequest):
    """Request for releasing/publishing a new MCP server to the registry"""
    # Basic server information specification
    serverSpecification: Optional[McpServerBasicInfo] = None
    # Tool specification defining the capabilities of the MCP server
    toolSpecification: Optional[PhnixMcpToolSpecification] = None
    # Endpoint specification for accessing the MCP server
    endpointSpecification: Optional[McpEndpointSpec] = None


class PhnixMcpServerDetailInfo(McpServerDetailInfo):
    """Detailed information about an MCP server including endpoints and tools"""
    # List of backend endpoints for internal server communication
    backendEndpoints: Optional[List[McpEndpointInfo]] = None
    # List of frontend endpoints for client access
    frontendEndpoints: Optional[List[McpEndpointInfo]] = None
    # Complete tool specification provided by the server
    toolSpec: Optional[PhnixMcpToolSpecification] = None
    # List of all available versions of the server
    allVersions: Optional[List[ServerVersionDetail]] = None
    # Namespace ID where the server is registered
    namespaceId: Optional[str] = None


class PhnixSubscribeMcpServerParam(SubscribeMcpServerParam):
    """Parameter model for subscribing to MCP server changes"""
    # Name of the MCP server to subscribe to
    mcp_name: Optional[str] = None
    # Version of the MCP server to subscribe to
    version: Optional[str] = None
    # Callback function to handle MCP server changes
    # Parameters: mcp_id, namespace_id, mcp_name, mcp_server_detail_info
    subscribe_callback: Optional[
        Callable[[str, str, str, PhnixMcpServerDetailInfo], Awaitable[None]]] = None
