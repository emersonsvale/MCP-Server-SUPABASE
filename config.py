"""
Configurações dinâmicas do servidor MCP Supabase
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Classe de configuração centralizada com suporte dinâmico"""
    
    def __init__(self, project_code: str = None, access_token: str = None):
        # Configurações padrão do Supabase (fallback)
        self.default_supabase_url = os.getenv("DEFAULT_SUPABASE_URL")
        self.default_supabase_key = os.getenv("DEFAULT_SUPABASE_ANON_KEY")
        self.default_supabase_service_key = os.getenv("DEFAULT_SUPABASE_SERVICE_KEY")
        
        # Configurações dinâmicas
        self.project_code = project_code
        self.access_token = access_token
        
        # Configurações do servidor
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        # Se não houver configuração dinâmica, usar padrão
        if not self.project_code and not self.default_supabase_url:
            raise ValueError("Nenhuma configuração do Supabase fornecida")
    
    def get_supabase_config(self) -> dict:
        """Retorna configuração do Supabase baseada no contexto"""
        if self.project_code and self.access_token:
            # Configuração dinâmica
            return {
                "url": f"https://{self.project_code}.supabase.co",
                "key": self.access_token,
                "service_key": self.access_token  # Usar o mesmo token como service key
            }
        else:
            # Configuração padrão
            return {
                "url": self.default_supabase_url,
                "key": self.default_supabase_key,
                "service_key": self.default_supabase_service_key
            }
    
    def get_supabase_url(self) -> str:
        """Retorna URL do Supabase"""
        config = self.get_supabase_config()
        return config["url"]
    
    def get_supabase_key(self) -> str:
        """Retorna chave do Supabase"""
        config = self.get_supabase_config()
        return config["key"]
    
    def get_supabase_service_key(self) -> str:
        """Retorna chave de serviço do Supabase"""
        config = self.get_supabase_config()
        return config["service_key"]
    
    def is_dynamic_config(self) -> bool:
        """Verifica se está usando configuração dinâmica"""
        return bool(self.project_code and self.access_token)
    
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return not self.debug 