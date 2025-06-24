"""
Ferramentas MCP para armazenamento de arquivos do Supabase
"""

import asyncio
import base64
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from supabase_client import SupabaseClient
from config import Config
from middleware import DynamicConfigMiddleware

class StorageTools:
    """Ferramentas para operações de armazenamento"""
    
    def __init__(self, middleware: DynamicConfigMiddleware):
        self.middleware = middleware
    
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
        # Atualizar configuração se project_code e access_token foram fornecidos
        project_code = arguments.get("project_code")
        access_token = arguments.get("access_token")
        
        if project_code and access_token:
            self.middleware.update_config_from_headers({
                "x-supabase-project": project_code,
                "x-supabase-token": access_token
            })
        
        # Obter config atual e criar client dinâmico
        config = self.middleware.get_current_config()
        client = SupabaseClient(config)
        
        if name == "storage_upload":
            return await self._execute_upload(client, arguments)
        elif name == "storage_download":
            return await self._execute_download(client, arguments)
        elif name == "storage_list_files":
            return await self._execute_list_files(client, arguments)
        elif name == "storage_delete_file":
            return await self._execute_delete_file(client, arguments)
        elif name == "storage_get_url":
            return await self._execute_get_url(client, arguments)
        elif name == "storage_list_buckets":
            return await self._execute_list_buckets(client, arguments)
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")
    
    async def _execute_upload(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Executa upload de arquivo"""
        bucket = args["bucket"]
        path = args["path"]
        file_data_b64 = args["file_data"]
        content_type = args.get("content_type", "application/octet-stream")
        
        try:
            # Decodificar dados base64
            file_data = base64.b64decode(file_data_b64)
            
            result = await client.upload_file(bucket, path, file_data, content_type)
            return [TextContent(
                type="text",
                text=f"Arquivo enviado com sucesso para {bucket}/{path}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao fazer upload do arquivo: {str(e)}"
            )]
    
    async def _execute_download(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Executa download de arquivo"""
        bucket = args["bucket"]
        path = args["path"]
        
        try:
            file_data = await client.download_file(bucket, path)
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
    
    async def _execute_list_files(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Lista arquivos em um bucket"""
        bucket = args["bucket"]
        path = args.get("path", "")
        
        try:
            result = client.client.storage.from_(bucket).list(path)
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
    
    async def _execute_delete_file(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Deleta um arquivo"""
        bucket = args["bucket"]
        path = args["path"]
        
        try:
            client.client.storage.from_(bucket).remove([path])
            return [TextContent(
                type="text",
                text=f"Arquivo {bucket}/{path} deletado com sucesso"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao deletar arquivo: {str(e)}"
            )]
    
    async def _execute_get_url(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Obtém URL pública de um arquivo"""
        bucket = args["bucket"]
        path = args["path"]
        
        try:
            url = client.client.storage.from_(bucket).get_public_url(path)
            return [TextContent(
                type="text",
                text=f"URL pública do arquivo: {url}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao obter URL do arquivo: {str(e)}"
            )]
    
    async def _execute_list_buckets(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Lista todos os buckets"""
        try:
            result = client.client.storage.list_buckets()
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