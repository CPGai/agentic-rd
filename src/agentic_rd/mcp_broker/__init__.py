# /home/carlospg/workspace/agentic-rd/src/agentic_rd/mcp_broker/__init__.py              
"""MCP Security Broker — confused-deputy defense interceptor."""              

from .broker import McpSecurityBroker              
from .errors import BrokerError, jsonrpc_error              

__all__ = ["McpSecurityBroker", "BrokerError", "jsonrpc_error"]              
__version__ = "3.0.0"
