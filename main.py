#!/usr/bin/env python3
"""
MCP Server para Supabase com configuração dinâmica
Fornece integração completa com Supabase através do Model Context Protocol
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# Importar nossas ferramentas
from tools.database import DatabaseTools
from tools.auth import AuthTools
from tools.storage import StorageTools
from tools.realtime import RealtimeTools
from config import Config
from middleware import DynamicConfigMiddleware

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseMCPServer:
    """Servidor MCP para integração com Supabase com configuração dinâmica"""
    
    def __init__(self):
        self.server = Server("supabase-mcp")
        
        # Configuração padrão
        default_config = Config()
        
        # Middleware para configuração dinâmica
        self.middleware = DynamicConfigMiddleware(default_config)
        
        # Inicializar ferramentas com middleware
        self.database_tools = DatabaseTools(self.middleware)
        self.auth_tools = AuthTools(self.middleware)
        self.storage_tools = StorageTools(self.middleware)
        self.realtime_tools = RealtimeTools(self.middleware)
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configurar handlers do servidor MCP"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Lista todas as ferramentas disponíveis"""
            tools = []
            
            # Adicionar ferramentas de banco de dados
            tools.extend(self.database_tools.get_tools())
            
            # Adicionar ferramentas de autenticação
            tools.extend(self.auth_tools.get_tools())
            
            # Adicionar ferramentas de armazenamento
            tools.extend(self.storage_tools.get_tools())
            
            # Adicionar ferramentas de tempo real
            tools.extend(self.realtime_tools.get_tools())
            
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Executa uma ferramenta específica com configuração dinâmica"""
            try:
                logger.info(f"Executando ferramenta: {name} com argumentos: {arguments}")
                
                # Atualizar configuração baseada nos headers
                if self.middleware.update_config_from_headers(arguments.get('headers', {})):
                    # Recriar ferramentas com nova configuração
                    self.database_tools = DatabaseTools(self.middleware)
                    self.auth_tools = AuthTools(self.middleware)
                    self.storage_tools = StorageTools(self.middleware)
                    self.realtime_tools = RealtimeTools(self.middleware)
                
                # Roteamento para ferramentas de banco de dados
                if name.startswith("database_"):
                    return await self.database_tools.execute_tool(name, arguments)
                
                # Roteamento para ferramentas de autenticação
                elif name.startswith("auth_"):
                    return await self.auth_tools.execute_tool(name, arguments)
                
                # Roteamento para ferramentas de armazenamento
                elif name.startswith("storage_"):
                    return await self.storage_tools.execute_tool(name, arguments)
                
                # Roteamento para ferramentas de tempo real
                elif name.startswith("realtime_"):
                    return await self.realtime_tools.execute_tool(name, arguments)
                
                else:
                    raise ValueError(f"Ferramenta desconhecida: {name}")
                    
            except Exception as e:
                logger.error(f"Erro ao executar ferramenta {name}: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"Erro: {str(e)}"
                )]

async def main():
    """Função principal do servidor MCP"""
    try:
        # Criar instância do servidor
        mcp_server = SupabaseMCPServer()
        
        # Configurar opções de inicialização
        init_options = InitializationOptions(
            server_name="supabase-mcp",
            server_version="1.0.0",
            capabilities={
                "tools": {}
            }
        )
        
        # Iniciar servidor
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.server.run(
                read_stream,
                write_stream,
                init_options
            )
            
    except Exception as e:
        logger.error(f"Erro fatal no servidor MCP: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 