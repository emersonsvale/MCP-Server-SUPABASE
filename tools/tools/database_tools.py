"""
Implementação modularizada: as operações de banco de dados estão agora em submódulos dentro de tools/database/.

Ferramentas MCP para operações de banco de dados do Supabase com configuração dinâmica
"""

import asyncio
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from middleware import DynamicConfigMiddleware
from supabase_client import SupabaseClient
from config import Config
from tools.database.queries import execute_query
from tools.database.inserts import execute_insert
from tools.database.updates import execute_update
from tools.database.deletes import execute_delete
from tools.database.tables import execute_list_tables, execute_get_project_info

class DatabaseTools:
    """Ferramentas para operações de banco de dados (configuração fixa)"""
    def __init__(self, config: Config, supabase_client: SupabaseClient):
        self.config = config
        self.client = supabase_client
    
    def get_tools(self) -> List[Tool]:
        """Retorna lista de ferramentas disponíveis (sem parâmetros dinâmicos)"""
        return [
            Tool(
                name="database_query",
                description="Executa uma consulta SQL personalizada no banco de dados Supabase",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "Query SQL a ser executada"
                        }
                    },
                    "required": ["sql"]
                }
            ),
            Tool(
                name="database_select",
                description="Seleciona registros de uma tabela com filtros opcionais",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "Nome da tabela"
                        },
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Colunas a serem selecionadas (deixe vazio para todas)"
                        },
                        "filters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "column": {"type": "string"},
                                    "operator": {"type": "string"},
                                    "value": {"type": "string"}
                                }
                            },
                            "description": "Filtros a serem aplicados"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Limite de registros"
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Offset para paginação"
                        }
                    },
                    "required": ["table"]
                }
            ),
            Tool(
                name="database_insert",
                description="Insere um novo registro em uma tabela",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "Nome da tabela"
                        },
                        "data": {
                            "type": "object",
                            "description": "Dados a serem inseridos"
                        }
                    },
                    "required": ["table", "data"]
                }
            ),
            Tool(
                name="database_update",
                description="Atualiza um registro existente",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "Nome da tabela"
                        },
                        "id": {
                            "type": "string",
                            "description": "ID do registro"
                        },
                        "data": {
                            "type": "object",
                            "description": "Dados a serem atualizados"
                        }
                    },
                    "required": ["table", "id", "data"]
                }
            ),
            Tool(
                name="database_delete",
                description="Deleta um registro",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "Nome da tabela"
                        },
                        "id": {
                            "type": "string",
                            "description": "ID do registro"
                        }
                    },
                    "required": ["table", "id"]
                }
            ),
            Tool(
                name="database_list_tables",
                description="Lista todas as tabelas disponíveis no banco de dados",
                inputSchema={}
            ),
            Tool(
                name="database_get_project_info",
                description="Obtém informações do projeto Supabase atual",
                inputSchema={}
            )
        ]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        dispatch = {
            "database_query": execute_query,
            "database_select": execute_select,
            "database_insert": execute_insert,
            "database_update": execute_update,
            "database_delete": execute_delete,
            "database_list_tables": execute_list_tables,
            "database_get_project_info": execute_get_project_info,
        }
        if name not in dispatch:
            raise ValueError(f"Ferramenta desconhecida: {name}")
        return await dispatch[name](self.client, arguments)

# TODO: Migrar o mesmo padrão de modularização para os módulos auth, storage e realtime para manter a consistência.
