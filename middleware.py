"""
Middleware para capturar headers e configurar Supabase dinamicamente
"""

import logging
from typing import Dict, Any, Optional
from mcp.types import CallToolRequest, ListToolsRequest
from config import Config
from supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class DynamicConfigMiddleware:
    """Middleware para configuração dinâmica do Supabase"""
    
    def __init__(self, default_config: Config):
        self.default_config = default_config
        self.current_config = default_config
        self.current_client = SupabaseClient(default_config)
    
    def extract_headers_from_request(self, request: Any) -> Dict[str, str]:
        """Extrai headers relevantes da requisição MCP"""
        headers = {}
        
        # Tentar extrair headers de diferentes tipos de requisição
        if hasattr(request, 'headers'):
            headers = request.headers
        elif hasattr(request, 'metadata'):
            headers = request.metadata
        elif hasattr(request, 'context'):
            headers = request.context
        
        return headers or {}
    
    def update_config_from_headers(self, headers: Dict[str, str]) -> bool:
        """Atualiza configuração baseada nos headers"""
        try:
            # Extrair project_code e access_token dos headers
            project_code = headers.get('x-supabase-project')
            access_token = headers.get('x-supabase-token')
            
            # Se não houver headers específicos, tentar formatos alternativos
            if not project_code:
                project_code = headers.get('supabase-project')
            if not access_token:
                access_token = headers.get('supabase-token')
            
            # Se ainda não encontrou, tentar Authorization header
            if not access_token:
                auth_header = headers.get('authorization', '')
                if auth_header.startswith('Bearer '):
                    access_token = auth_header[7:]  # Remove 'Bearer '
            
            # Se encontrou configuração dinâmica, atualizar
            if project_code and access_token:
                logger.info(f"Atualizando configuração para projeto: {project_code}")
                
                # Criar nova configuração
                new_config = Config(project_code, access_token)
                
                # Atualizar cliente
                self.current_config = new_config
                self.current_client.update_config(project_code, access_token)
                
                return True
            else:
                # Usar configuração padrão
                if self.current_config != self.default_config:
                    logger.info("Revertendo para configuração padrão")
                    self.current_config = self.default_config
                    self.current_client = SupabaseClient(self.default_config)
                
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração: {str(e)}")
            return False
    
    def get_current_client(self) -> SupabaseClient:
        """Retorna o cliente atual"""
        return self.current_client
    
    def get_current_config(self) -> Config:
        """Retorna a configuração atual"""
        return self.current_config 