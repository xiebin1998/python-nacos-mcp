import asyncio
import logging
from typing import Dict, Optional

from v2.nacos.ai.model.cache.mcp_server_info_cache import McpServerInfoCacheHolder
from v2.nacos.ai.model.cache.mcp_server_subscribe_manager import \
    McpServerSubscribeManager
from v2.nacos.ai.model.mcp.mcp import McpServerDetailInfo
from v2.nacos.ai.util.mcp_server_util import build_mcp_server_key
from v2.nacos.common.constants import Constants

from phnix_nacos_mcp.mcp_server_subscribe_manager import PhnixMcpServerSubscribeManager
from phnix_nacos_mcp.model.mcp_param import PhnixMcpServerDetailInfo


class PhnixMcpServerInfoCacheHolder(McpServerInfoCacheHolder):

    def __init__(self, subscribe_manager: PhnixMcpServerSubscribeManager, ai_proxy):
        super().__init__(subscribe_manager, ai_proxy)
        self.mcp_server_cache: Dict[str, PhnixMcpServerDetailInfo] = {}

    async def get_mcp_server(self, mcp_name: str, version: str) -> Optional[PhnixMcpServerDetailInfo]:
        key = build_mcp_server_key(mcp_name, version)
        async with self.cache_lock:
            if key in self.mcp_server_cache:
                return self.mcp_server_cache[key]
            else:
                return None

    async def add_mcp_server_update_task(self, mcp_name: str, version: str):
        key = build_mcp_server_key(mcp_name, version)
        if key not in self.task:
            self.task[key] = asyncio.create_task(self.update_mcp_server(mcp_name, version))

    async def process_mcp_server_detail_info(self, mcp_server_detail_info: PhnixMcpServerDetailInfo):
        mcp_name = mcp_server_detail_info.name
        version = mcp_server_detail_info.versionDetail.version
        is_latest = mcp_server_detail_info.versionDetail.is_latest
        key = build_mcp_server_key(mcp_name, version)
        async with self.cache_lock:
            old_mcp_server = self.mcp_server_cache.get(key)
            self.mcp_server_cache[key] = mcp_server_detail_info
            if is_latest is not None and is_latest:
                latest_key = build_mcp_server_key(mcp_name, None)
                self.mcp_server_cache[latest_key] = mcp_server_detail_info

        if old_mcp_server is None or self.is_mcp_server_changed(old_mcp_server,
                                                                mcp_server_detail_info):
            for callback_func in self.mcp_server_subscribe_manager.subscribers.get(
                    key, []):
                await callback_func(mcp_server_detail_info.id,
                                    mcp_server_detail_info.namespaceId,
                                    mcp_server_detail_info.name,
                                    mcp_server_detail_info)
            if is_latest is not None and is_latest:
                for callback_func in self.mcp_server_subscribe_manager.subscribers.get(
                        latest_key, []):
                    await callback_func(mcp_server_detail_info.id,
                                        mcp_server_detail_info.namespaceId,
                                        mcp_server_detail_info.name,
                                        mcp_server_detail_info)
