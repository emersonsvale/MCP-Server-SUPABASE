"""
Cliente Supabase centralizado com suporte dinâmico
"""

import asyncio
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from config import Config

class SupabaseClient:
    """Cliente Supabase com métodos assíncronos e configuração dinâmica"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente Supabase com configuração dinâmica"""
        try:
            supabase_url = self.config.get_supabase_url()
            supabase_key = self.config.get_supabase_key()
            
            if not supabase_url or not supabase_key:
                raise Exception("URL ou chave do Supabase não configuradas")
            
            self.client = create_client(supabase_url, supabase_key)
            
        except Exception as e:
            raise Exception(f"Erro ao inicializar cliente Supabase: {str(e)}")
    
    def update_config(self, project_code: str, access_token: str):
        """Atualiza configuração dinamicamente"""
        self.config.project_code = project_code
        self.config.access_token = access_token
        self._initialize_client()
    
    async def query_table(self, table: str, query_params: Dict[str, Any] = None) -> List[Dict]:
        """Executa query em uma tabela"""
        try:
            query = self.client.table(table).select("*")
            
            if query_params:
                # Aplicar filtros
                if "filters" in query_params:
                    for filter_item in query_params["filters"]:
                        query = query.filter(filter_item["column"], filter_item["operator"], filter_item["value"])
                
                # Aplicar ordenação
                if "order_by" in query_params:
                    query = query.order(query_params["order_by"]["column"], desc=query_params["order_by"].get("desc", False))
                
                # Aplicar paginação
                if "limit" in query_params:
                    query = query.limit(query_params["limit"])
                if "offset" in query_params:
                    query = query.range(query_params["offset"], query_params["offset"] + query_params.get("limit", 100) - 1)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            raise Exception(f"Erro ao consultar tabela {table}: {str(e)}")
    
    async def insert_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insere um registro em uma tabela"""
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            raise Exception(f"Erro ao inserir registro na tabela {table}: {str(e)}")
    
    async def update_record(self, table: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza um registro"""
        try:
            result = self.client.table(table).update(data).eq("id", record_id).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            raise Exception(f"Erro ao atualizar registro na tabela {table}: {str(e)}")
    
    async def delete_record(self, table: str, record_id: str) -> bool:
        """Deleta um registro"""
        try:
            result = self.client.table(table).delete().eq("id", record_id).execute()
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"Erro ao deletar registro na tabela {table}: {str(e)}")
    
    async def sign_up(self, email: str, password: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Registra um novo usuário"""
        try:
            result = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            return result.user.__dict__ if result.user else {}
        except Exception as e:
            raise Exception(f"Erro ao registrar usuário: {str(e)}")
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Faz login do usuário"""
        try:
            result = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return result.user.__dict__ if result.user else {}
        except Exception as e:
            raise Exception(f"Erro ao fazer login: {str(e)}")
    
    async def sign_out(self) -> bool:
        """Faz logout do usuário"""
        try:
            self.client.auth.sign_out()
            return True
        except Exception as e:
            raise Exception(f"Erro ao fazer logout: {str(e)}")
    
    async def upload_file(self, bucket: str, path: str, file_data: bytes, content_type: str = None) -> Dict[str, Any]:
        """Faz upload de um arquivo"""
        try:
            result = self.client.storage.from_(bucket).upload(
                path=path,
                file=file_data,
                file_options={"content-type": content_type} if content_type else {}
            )
            return result
        except Exception as e:
            raise Exception(f"Erro ao fazer upload do arquivo: {str(e)}")
    
    async def download_file(self, bucket: str, path: str) -> bytes:
        """Faz download de um arquivo"""
        try:
            result = self.client.storage.from_(bucket).download(path)
            return result
        except Exception as e:
            raise Exception(f"Erro ao fazer download do arquivo: {str(e)}") 