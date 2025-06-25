from mcp.types import TextContent

async def execute_list_tables(client, args):
    try:
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

async def execute_get_project_info(client, args):
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