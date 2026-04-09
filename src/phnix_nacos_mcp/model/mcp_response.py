from typing import Optional

from v2.nacos.ai.model.ai_response import QueryMcpServerResponse

from phnix_nacos_mcp.model.mcp_param import PhnixMcpServerDetailInfo


class PhnixQueryMcpServerResponse(QueryMcpServerResponse):
	"""Response for MCP server query requests"""
	# Detailed information about the queried MCP server
	mcpServerDetailInfo: Optional[PhnixMcpServerDetailInfo] = None