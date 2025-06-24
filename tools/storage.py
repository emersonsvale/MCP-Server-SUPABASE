"""
Ferramentas MCP para armazenamento de arquivos do Supabase
"""

import asyncio
import base64
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from supabase_client import SupabaseClient
from config import Config

class StorageTools:
    """Ferramentas para operações de armazenamento"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = SupabaseClient(config)
    
    def get_tools(self) -> List[Tool]:
        """Retorna lista de ferramentas disponíveis"""
        return [
            Tool(
                name="storage_upload",
                description="Faz upload de um arquivo para o Supabase Storage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bucket": {
                            "type": "string",
                            "description": "Nome do bucket"
                        },
                        "path": {
                            "type": "string",
                            "description": "Caminho do arquivo no bucket"
                        },
                        "file_data": {
                            "type": "string",
                            "description": "Dados do arquivo em base64"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Tipo de conteúdo do arquivo"
                        }
                    },
                    "required": ["bucket", "path", "file_data"]
                }
            ),
            Tool(
                name="storage_download",
                description="Faz download de um arquivo do Supabase Storage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bucket": {
                            "type": "string",
                            "description": "Nome do bucket"
                        },
                        "path": {
                            "type": "string",
                            "description": "Caminho do arquivo no bucket"
                        }
                    },
                    "required": ["bucket", "path"]
                }
            ),
            Tool(
                name="storage_list_files",
                description="Lista arquivos em um bucket",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bucket": {
                            "type": "string",
                            "description": "Nome do bucket"
                        },
                        "path": {
                            "type": "string",
                            "description": "Caminho para listar (opcional)"
                        }
                    },
                    "required": ["bucket"]
                }
            ),
            Tool(
                name="storage_delete_file",
                description="Deleta um arquivo do Supabase Storage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bucket": {
                            "type": "string",
                            "description": "Nome do bucket"
                        },
                        "path": {
                            "type": "string",
                            "description": "Caminho do arquivo no bucket"
                        }
                    },
                    "required": ["bucket", "path"]
                }
            ),
            Tool(
                name="storage_get_url",
                description="Obtém URL pública de um arquivo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bucket": {
                            "type": "string",
                            "description": "Nome do bucket"
                        },
                        "path": {
                            "type": "string",
                            "description": "Caminho do arquivo no bucket"
                        }
                    },
                    "required": ["bucket", "path"]
                }
            ),
            Tool(
                name="storage_list_buckets",
                description="Lista todos os buckets disponíveis",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Executa uma ferramenta específica"""
        if name == "storage_upload":
            return await self._execute_upload(arguments)
        elif name == "storage_download":
            return await self._execute_download(arguments)
        elif name == "storage_list_files":
            return await self._execute_list_files(arguments)
        elif name == "storage_delete_file":
            return await self._execute_delete_file(arguments)
        elif name == "storage_get_url":
            return await self._execute_get_url(arguments)
        elif name == "storage_list_buckets":
            return await self._execute_list_buckets(arguments)
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")
    
    async def _execute_upload(self, args: Dict[str, Any]) -> List[TextContent]:
        """Executa upload de arquivo"""
        bucket = args["bucket"]
        path = args["path"]
        file_data_b64 = args["file_data"]
        content_type = args.get("content_type", "application/octet-stream")
        
        try:
            # Decodificar dados base64
            file_data = base64.b64decode(file_data_b64)
            
            result = await self.client.upload_file(bucket, path, file_data, content_type)
            return [TextContent(
                type="text",
                text=f"Arquivo enviado com sucesso para {bucket}/{path}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao fazer upload do arquivo: {str(e)}"
            )]
    
    async def _execute_download(self, args: Dict[str, Any]) -> List[TextContent]:
        """Executa download de arquivo"""
        bucket = args["bucket"]
        path = args["path"]
        
        try:
            file_data = await self.client.download_file(bucket, path)
            file_data_b64 = base64.b64encode(file_data).decode('utf-8')
            
            return [TextContent(
                type="text",
                text=f"Arquivo baixado com sucesso. Dados em base64: {file_data_b64[:100]}..."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao fazer download do arquivo: {str(e)}"
            )]
    
    async def _execute_list_files(self, args: Dict[str, Any]) -> List[TextContent]:
        """Lista arquivos em um bucket"""
        bucket = args["bucket"]
        path = args.get("path", "")
        
        try:
            result = self.client.client.storage.from_(bucket).list(path)
            files = [item["name"] for item in result] if result else []
            
            return [TextContent(
                type="text",
                text=f"Arquivos em {bucket}/{path}:\n{', '.join(files)}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao listar arquivos: {str(e)}"
            )]
    
    async def _execute_delete_file(self, args: Dict[str, Any]) -> List[TextContent]:
        """Deleta um arquivo"""
        bucket = args["bucket"]
        path = args["path"]
        
        try:
            self.client.client.storage.from_(bucket).remove([path])
            return [TextContent(
                type="text",
                text=f"Arquivo {bucket}/{path} deletado com sucesso"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao deletar arquivo: {str(e)}"
            )]
    
    async def _execute_get_url(self, args: Dict[str, Any]) -> List[TextContent]:
        """Obtém URL pública de um arquivo"""
        bucket = args["bucket"]
        path = args["path"]
        
        try:
            url = self.client.client.storage.from_(bucket).get_public_url(path)
            return [TextContent(
                type="text",
                text=f"URL pública do arquivo: {url}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao obter URL do arquivo: {str(e)}"
            )]
    
    async def _execute_list_buckets(self, args: Dict[str, Any]) -> List[TextContent]:
        """Lista todos os buckets"""
        try:
            result = self.client.client.storage.list_buckets()
            buckets = [bucket["name"] for bucket in result] if result else []
            
            return [TextContent(
                type="text",
                text=f"Buckets disponíveis:\n{', '.join(buckets)}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao listar buckets: {str(e)}"
            )] 