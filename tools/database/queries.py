from mcp.types import TextContent

async def execute_query(client, args):
    sql = args["sql"]
    try:
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

async def execute_select(client, args):
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