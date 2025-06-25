from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from tools.database_tools import DatabaseTools
from tools.auth import AuthTools
from tools.storage import StorageTools
from tools.realtime import RealtimeTools
from config import Config
from supabase_client import SupabaseClient
from middleware import DynamicConfigMiddleware
import logging

app = FastAPI(title="MCP Server Supabase", version="1.0.0")

# Configuração padrão
default_config = Config()
middleware = DynamicConfigMiddleware(default_config)

# Instâncias fixas (fallback)
def get_tools_instances(config: Config, client: SupabaseClient):
    return {
        "database": DatabaseTools(config, client),
        "auth": AuthTools(config, client),
        "storage": StorageTools(config, client),
        "realtime": RealtimeTools(config, client),
    }

@app.middleware("http")
async def dynamic_config_middleware(request: Request, call_next):
    headers = dict(request.headers)
    middleware.update_config_from_headers(headers)
    response = await call_next(request)
    return response

@app.get("/mcp/list_tools")
async def list_tools(request: Request):
    client = middleware.get_current_client()
    config = middleware.get_current_config()
    tools_instances = get_tools_instances(config, client)
    tools = []
    tools.extend(tools_instances["database"].get_tools())
    tools.extend(tools_instances["auth"].get_tools())
    tools.extend(tools_instances["storage"].get_tools())
    tools.extend(tools_instances["realtime"].get_tools())
    return [tool.model_dump() if hasattr(tool, "model_dump") else tool.__dict__ for tool in tools]

@app.post("/mcp/call_tool")
async def call_tool(request: Request, name: str = None, arguments: Dict[str, Any] = None):
    try:
        body = await request.json()
        name = name or body.get("name")
        arguments = arguments or body.get("arguments", {})
        if not name:
            raise HTTPException(status_code=400, detail="Nome da ferramenta é obrigatório.")
        client = middleware.get_current_client()
        config = middleware.get_current_config()
        tools_instances = get_tools_instances(config, client)
        # Roteamento
        if name.startswith("database_"):
            result = await tools_instances["database"].execute_tool(name, arguments)
        elif name.startswith("auth_"):
            result = await tools_instances["auth"].execute_tool(name, arguments)
        elif name.startswith("storage_"):
            result = await tools_instances["storage"].execute_tool(name, arguments)
        elif name.startswith("realtime_"):
            result = await tools_instances["realtime"].execute_tool(name, arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Ferramenta desconhecida: {name}")
        # Serializar resultado
        return JSONResponse(content=[r.__dict__ for r in result])
    except Exception as e:
        logging.exception("Erro ao executar ferramenta")
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI já expõe /docs e /openapi.json automaticamente 
