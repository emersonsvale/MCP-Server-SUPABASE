"""
Ferramentas MCP para autenticação do Supabase
"""

import asyncio
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from supabase_client import SupabaseClient
from config import Config
from middleware import DynamicConfigMiddleware

class AuthTools:
    """Ferramentas para operações de autenticação (configuração fixa)"""
    def __init__(self, config: Config, supabase_client: SupabaseClient):
        self.config = config
        self.client = supabase_client
    
    def get_tools(self) -> List[Tool]:
        """Retorna lista de ferramentas disponíveis"""
        return [
            Tool(
                name="auth_sign_up",
                description="Registra um novo usuário no Supabase",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email do usuário"
                        },
                        "password": {
                            "type": "string",
                            "description": "Senha do usuário"
                        },
                        "user_data": {
                            "type": "object",
                            "description": "Dados adicionais do usuário"
                        }
                    },
                    "required": ["email", "password"]
                }
            ),
            Tool(
                name="auth_sign_in",
                description="Faz login de um usuário",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email do usuário"
                        },
                        "password": {
                            "type": "string",
                            "description": "Senha do usuário"
                        }
                    },
                    "required": ["email", "password"]
                }
            ),
            Tool(
                name="auth_sign_out",
                description="Faz logout do usuário atual",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="auth_get_user",
                description="Obtém informações do usuário atual",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="auth_reset_password",
                description="Solicita reset de senha",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email do usuário"
                        }
                    },
                    "required": ["email"]
                }
            ),
            Tool(
                name="auth_update_user",
                description="Atualiza dados do usuário atual",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_data": {
                            "type": "object",
                            "description": "Novos dados do usuário"
                        }
                    },
                    "required": ["user_data"]
                }
            )
        ]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Executa uma ferramenta específica"""
        if name == "auth_sign_up":
            return await self._execute_sign_up(self.client, arguments)
        elif name == "auth_sign_in":
            return await self._execute_sign_in(self.client, arguments)
        elif name == "auth_sign_out":
            return await self._execute_sign_out(self.client, arguments)
        elif name == "auth_get_user":
            return await self._execute_get_user(self.client, arguments)
        elif name == "auth_reset_password":
            return await self._execute_reset_password(self.client, arguments)
        elif name == "auth_update_user":
            return await self._execute_update_user(self.client, arguments)
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")
    
    async def _execute_sign_up(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Executa registro de usuário"""
        email = args["email"]
        password = args["password"]
        user_data = args.get("user_data", {})
        
        try:
            result = await client.sign_up(email, password, user_data)
            return [TextContent(
                type="text",
                text=f"Usuário registrado com sucesso:\n{result}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao registrar usuário: {str(e)}"
            )]
    
    async def _execute_sign_in(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Executa login de usuário"""
        email = args["email"]
        password = args["password"]
        
        try:
            result = await client.sign_in(email, password)
            return [TextContent(
                type="text",
                text=f"Login realizado com sucesso:\n{result}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao fazer login: {str(e)}"
            )]
    
    async def _execute_sign_out(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Executa logout de usuário"""
        try:
            result = await client.sign_out()
            return [TextContent(
                type="text",
                text="Logout realizado com sucesso"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao fazer logout: {str(e)}"
            )]
    
    async def _execute_get_user(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Obtém informações do usuário atual"""
        try:
            user = client.client.auth.get_user()
            return [TextContent(
                type="text",
                text=f"Usuário atual:\n{user.user.__dict__ if user.user else 'Nenhum usuário logado'}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao obter usuário: {str(e)}"
            )]
    
    async def _execute_reset_password(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Solicita reset de senha"""
        email = args["email"]
        
        try:
            client.client.auth.reset_password_email(email)
            return [TextContent(
                type="text",
                text=f"Email de reset de senha enviado para {email}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao solicitar reset de senha: {str(e)}"
            )]
    
    async def _execute_update_user(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Atualiza dados do usuário"""
        user_data = args["user_data"]
        
        try:
            result = client.client.auth.update_user(user_data)
            return [TextContent(
                type="text",
                text=f"Usuário atualizado com sucesso:\n{result.user.__dict__ if result.user else 'Erro na atualização'}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao atualizar usuário: {str(e)}"
            )] 