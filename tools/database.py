"""
Ferramentas MCP para operações de banco de dados do Supabase com configuração dinâmica
"""

import asyncio
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from middleware import DynamicConfigMiddleware

class DatabaseTools:
    """Ferramentas para operações de banco de dados"""
    
    def __init__(self, middleware: DynamicConfigMiddleware):
        self.middleware = middleware
    
    def get_tools(self) -> List[Tool]:
        """Retorna lista de ferramentas disponíveis"""
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
                        },
                        "project_code": {
                            "type": "string",
                            "description": "Código do projeto Supabase (opcional, pode ser enviado via header)"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Token de acesso do Supabase (opcional, pode ser enviado via header)"
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
                        },
                        "project_code": {
                            "type": "string",
                            "description": "Código do projeto Supabase (opcional, pode ser enviado via header)"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Token de acesso do Supabase (opcional, pode ser enviado via header)"
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
                        },
                        "project_code": {
                            "type": "string",
                            "description": "Código do projeto Supabase (opcional, pode ser enviado via header)"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Token de acesso do Supabase (opcional, pode ser enviado via header)"
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
                        },
                        "project_code": {
                            "type": "string",
                            "description": "Código do projeto Supabase (opcional, pode ser enviado via header)"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Token de acesso do Supabase (opcional, pode ser enviado via header)"
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
                        },
                        "project_code": {
                            "type": "string",
                            "description": "Código do projeto Supabase (opcional, pode ser enviado via header)"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Token de acesso do Supabase (opcional, pode ser enviado via header)"
                        }
                    },
                    "required": ["table", "id"]
                }
            ),
            Tool(
                name="database_list_tables",
                description="Lista todas as tabelas disponíveis no banco de dados",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_code": {
                            "type": "string",
                            "description": "Código do projeto Supabase (opcional, pode ser enviado via header)"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Token de acesso do Supabase (opcional, pode ser enviado via header)"
                        }
                    }
                }
            ),
            Tool(
                name="database_get_project_info",
                description="Obtém informações do projeto Supabase atual",
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
        
        # Obter cliente atual
        client = self.middleware.get_current_client()
        
        if name == "database_query":
            return await self._execute_query(client, arguments)
        elif name == "database_select":
            return await self._execute_select(client, arguments)
        elif name == "database_insert":
            return await self._execute_insert(client, arguments)
        elif name == "database_update":
            return await self._execute_update(client, arguments)
        elif name == "database_delete":
            return await self._execute_delete(client, arguments)
        elif name == "database_list_tables":
            return await self._execute_list_tables(client, arguments)
        elif name == "database_get_project_info":
            return await self._execute_get_project_info(client, arguments)
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")
    
    async def _execute_query(self, client, args: Dict[str, Any]) -> List[TextContent]:
        """Executa query SQL personalizada"""
        sql = args["sql"]
        try:
            # Para queries personalizadas, usamos o cliente RPC
            result = client.client.rpc("exec_sql", {"sql_query": sql}).execute()
            return [TextContent(
                type="text",
                text=f"Query executada com sucesso. Resultado: {result.data}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao executar query: {str(e)}"
            )]
    
    async def _execute_select(self, client, args: Dict[str, Any]) -> List[TextContent]:
        """Executa seleção de dados"""
        table = args["table"]
        columns = args.get("columns", ["*"])
        filters = args.get("filters", [])
        limit = args.get("limit", 100)
        offset = args.get("offset", 0)
        
        try:
            query_params = {
                "filters": filters,
                "limit": limit,
                "offset": offset
            }
            
            result = await client.query_table(table, query_params)
            
            return [TextContent(
                type="text",
                text=f"Consulta executada com sucesso. Encontrados {len(result)} registros:\n{result}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao consultar tabela {table}: {str(e)}"
            )]
    
    async def _execute_insert(self, client, args: Dict[str, Any]) -> List[TextContent]:
        """Executa inserção de dados"""
        table = args["table"]
        data = args["data"]
        
        try:
            result = await client.insert_record(table, data)
            return [TextContent(
                type="text",
                text=f"Registro inserido com sucesso na tabela {table}:\n{result}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao inserir registro na tabela {table}: {str(e)}"
            )]
    
    async def _execute_update(self, client, args: Dict[str, Any]) -> List[TextContent]:
        """Executa atualização de dados"""
        table = args["table"]
        record_id = args["id"]
        data = args["data"]
        
        try:
            result = await client.update_record(table, record_id, data)
            return [TextContent(
                type="text",
                text=f"Registro atualizado com sucesso na tabela {table}:\n{result}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao atualizar registro na tabela {table}: {str(e)}"
            )]
    
    async def _execute_delete(self, client, args: Dict[str, Any]) -> List[TextContent]:
        """Executa deleção de dados"""
        table = args["table"]
        record_id = args["id"]
        
        try:
            result = await client.delete_record(table, record_id)
            return [TextContent(
                type="text",
                text=f"Registro deletado com sucesso da tabela {table}" if result else "Registro não encontrado"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao deletar registro da tabela {table}: {str(e)}"
            )]
    
    async def _execute_list_tables(self, client, args: Dict[str, Any]) -> List[TextContent]:
        """Lista todas as tabelas"""
        try:
            # Query para listar tabelas (PostgreSQL)
            sql = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
            result = client.client.rpc("exec_sql", {"sql_query": sql}).execute()
            
            tables = [row["table_name"] for row in result.data] if result.data else []
            
            return [TextContent(
                type="text",
                text=f"Tabelas disponíveis no banco de dados:\n{', '.join(tables)}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao listar tabelas: {str(e)}"
            )]
    
    async def _execute_get_project_info(self, client, args: Dict[str, Any]) -> List[TextContent]:
        """Obtém informações do projeto atual"""
        try:
            project_info = client.get_project_info()
            return [TextContent(
                type="text",
                text=f"Informações do projeto:\n{project_info}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao obter informações do projeto: {str(e)}"
            )] 