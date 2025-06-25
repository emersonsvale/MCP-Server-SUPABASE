from mcp.types import TextContent

async def execute_insert(client, args):
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