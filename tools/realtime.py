"""
Ferramentas MCP para funcionalidades de tempo real do Supabase
"""

import asyncio
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from supabase_client import SupabaseClient
from config import Config
from middleware import DynamicConfigMiddleware

class RealtimeTools:
    """Ferramentas para funcionalidades de tempo real (configuração fixa)"""
    def __init__(self, config: Config, supabase_client: SupabaseClient):
        self.config = config
        self.client = supabase_client
        self.subscriptions = {}
    
    def get_tools(self) -> List[Tool]:
        """Retorna lista de ferramentas disponíveis"""
        return [
            Tool(
                name="realtime_subscribe",
                description="Inscreve-se em mudanças de uma tabela em tempo real",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "Nome da tabela"
                        },
                        "event": {
                            "type": "string",
                            "enum": ["INSERT", "UPDATE", "DELETE", "*"],
                            "description": "Tipo de evento a ser monitorado"
                        },
                        "filter": {
                            "type": "string",
                            "description": "Filtro SQL opcional"
                        }
                    },
                    "required": ["table"]
                }
            ),
            Tool(
                name="realtime_unsubscribe",
                description="Cancela inscrição em mudanças de uma tabela",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "Nome da tabela"
                        }
                    },
                    "required": ["table"]
                }
            ),
            Tool(
                name="realtime_list_subscriptions",
                description="Lista todas as inscrições ativas",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="realtime_broadcast",
                description="Envia uma mensagem para um canal de broadcast",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Nome do canal"
                        },
                        "message": {
                            "type": "object",
                            "description": "Mensagem a ser enviada"
                        }
                    },
                    "required": ["channel", "message"]
                }
            ),
            Tool(
                name="realtime_subscribe_channel",
                description="Inscreve-se em um canal de broadcast",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Nome do canal"
                        }
                    },
                    "required": ["channel"]
                }
            )
        ]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Executa uma ferramenta específica"""
        if name == "realtime_subscribe":
            return await self._execute_subscribe(self.client, arguments)
        elif name == "realtime_unsubscribe":
            return await self._execute_unsubscribe(self.client, arguments)
        elif name == "realtime_list_subscriptions":
            return await self._execute_list_subscriptions(self.client, arguments)
        elif name == "realtime_broadcast":
            return await self._execute_broadcast(self.client, arguments)
        elif name == "realtime_subscribe_channel":
            return await self._execute_subscribe_channel(self.client, arguments)
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")
    
    async def _execute_subscribe(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Inscreve-se em mudanças de uma tabela"""
        table = args["table"]
        event = args.get("event", "*")
        filter_query = args.get("filter", "")
        
        try:
            # Criar subscription
            subscription = client.client.table(table).on(
                event, 
                callback=self._handle_table_change
            )
            
            if filter_query:
                subscription = subscription.filter(filter_query)
            
            # Armazenar subscription
            self.subscriptions[table] = subscription
            
            return [TextContent(
                type="text",
                text=f"Inscrição criada com sucesso para tabela {table}, evento {event}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao criar inscrição: {str(e)}"
            )]
    
    async def _execute_unsubscribe(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Cancela inscrição em uma tabela"""
        table = args["table"]
        
        try:
            if table in self.subscriptions:
                # Remover subscription
                del self.subscriptions[table]
                return [TextContent(
                    type="text",
                    text=f"Inscrição removida com sucesso para tabela {table}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Nenhuma inscrição encontrada para tabela {table}"
                )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao remover inscrição: {str(e)}"
            )]
    
    async def _execute_list_subscriptions(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Lista todas as inscrições ativas"""
        try:
            tables = list(self.subscriptions.keys())
            return [TextContent(
                type="text",
                text=f"Inscrições ativas: {', '.join(tables) if tables else 'Nenhuma'}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao listar inscrições: {str(e)}"
            )]
    
    async def _execute_broadcast(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Envia mensagem para um canal"""
        channel = args["channel"]
        message = args["message"]
        
        try:
            client.client.channel(channel).send(message)
            return [TextContent(
                type="text",
                text=f"Mensagem enviada com sucesso para o canal {channel}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao enviar mensagem: {str(e)}"
            )]
    
    async def _execute_subscribe_channel(self, client: SupabaseClient, args: Dict[str, Any]) -> List[TextContent]:
        """Inscreve-se em um canal de broadcast"""
        channel = args["channel"]
        
        try:
            # Criar subscription para canal
            subscription = client.client.channel(channel).on(
                "broadcast", 
                {"event": "message"}, 
                self._handle_channel_message
            ).subscribe()
            
            # Armazenar subscription
            self.subscriptions[f"channel_{channel}"] = subscription
            
            return [TextContent(
                type="text",
                text=f"Inscrição criada com sucesso para o canal {channel}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Erro ao criar inscrição no canal: {str(e)}"
            )] 